from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from werkzeug.security import check_password_hash, generate_password_hash
import xml.etree.ElementTree as ET
import uuid
import re
import random
import string
import tldextract
from app.auth import login_required
from app.db import get_db


bp = Blueprint('main', __name__)

@bp.route('/', methods = ['GET'])
@login_required
def index():
	db = get_db()

	if request.args.get('limit') in ['10', '20', '30', '50', '100']:
		limit = int(request.args.get('limit'))
	else:
		limit = 10

	if 'page' not in request.args:
		page = 1	
	else:
		try:
			page = int(request.args.get('page'))
		except ValueError:
			page = 1

	if 'search' not in request.args:
		search = '.*' 
	else:
		search = request.args.get('search').strip()
				
	projects = db.execute(
		'SELECT id, name FROM projects WHERE owner = ? AND name REGEXP ? LIMIT ? OFFSET ?', 
		(session['username'], search, limit, limit * (page - 1), )
	).fetchall()


	allprojects = db.execute(
		'SELECT id, name FROM projects WHERE owner = ? AND name REGEXP ?',
		(session['username'], search, )
	).fetchall()

	if len(allprojects) % limit == 0:
		pages = int(len(allprojects) / limit)
	else:
		pages = int(len(allprojects) / limit + 1)

	return render_template('main/main.html', username=session['username'], rows=projects, limit=limit, pages=pages, page=page, search=search)



@bp.route('/profile', methods = ['GET'])
@login_required
def profile():
	id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))
	return render_template('main/profile.html', username=session['username'], id=id)
	


@bp.route('/new', methods = ['GET', 'POST'])
@login_required
def new():
	db = get_db()
	if request.method == 'POST':
		errors = []
		warnings = []
		projectName = request.form['projectName']
		nmapFile = request.files['nmapFile']
		nmapXML = nmapFile.stream.read()
		masscanFile = request.files['masscanFile']
		masscanXML = masscanFile.stream.read()
		domainFile = request.files['domainFile']


		if not projectName:
			errors.append("Project name is required")

		if not nmapFile and not masscanFile and not domainFile:
			errors.append("Even one file is required")

		if not nmapFile:
			warnings.append("Nmap file was not uploaded")
		else:
			try:
				tree = ET.fromstring(nmapXML)
			except:
				errors.append("Nmap file is not valid xml file")	

		if not masscanFile:
			warnings.append("Masscan file was not uploaded")
		else:
			try:
				tree = ET.fromstring(masscanXML)
			except:
				errors.append("Masscan file is not a valid xml file")

		if not domainFile:
			warnings.append("Domain file was not uploaded")	
				
		if errors:
			return render_template('main/new.html', username=session['username'], errors=errors)
		

		# Fill database
		try:
			project = str(uuid.uuid4())
			db.execute(
				'INSERT INTO projects (id, name, owner) VALUES (?, ?, ?)',
				(project, projectName, session['username'])
			)
			if nmapFile:
				parseNmapFile(nmapXML, project, db)
			if masscanFile:
				parseMasscanFile(masscanXML, project, db)
			if domainFile:
				parseDomainFile(domainFile, project, db)
			db.commit()			
		except Exception as e:
			errors.append(str(e))
			return render_template('main/new.html', username=session['username'], errors=errors)
		
		success = "Project was successfully created"
		return render_template('main/new.html', username=session['username'], warnings=warnings, success=success)	

	else:
		return render_template('main/new.html', username=session['username'])

def parseNmapFile(file, project, db):
	scan = ET.fromstring(file)
	for host in scan.findall('host'):
		if host.find('status').get('state') != 'up':
			continue

		ip = host.find('address').get('addr')	
		hostCheck = db.execute(
			'SELECT * FROM hosts WHERE project = ? and ip = ?',
			(project, ip, )
		).fetchone()

		if hostCheck is None:
			hostid = str(uuid.uuid4())
			portsq = 0
			db.execute(
				'INSERT INTO hosts (id, ip, note, style, portsq, project) VALUES (?, ?, ?, ?, ?, ?)',
				(hostid, ip, "", "Default", portsq, project)
			)
		else:
			hostid = hostCheck['id']
			portsq = int(hostCheck['portsq'])


		for port in host.find('ports').findall('port'):
			if port.find('state').get('state') != 'open':
				continue

			p = port.get('portid')
			portcheck = db.execute(
				'SELECT * FROM ports WHERE host = ? and port = ?', 
				(hostid, p, )
			).fetchone()

			state = port.find('state').get('state')
			
			try:
				service = port.find('service').get('name')
			except Exception as e:
				service = ""
			
			try:
				version = port.find('service').get('product')
			except Exception:
				version = ""	
			
			try:
				if port.find('service').get('version'):
					version += " " + port.find('service').get('version')
			except Exception as e:
				version = ""
			

			if portcheck is None:
				portsq = 1
				portid = str(uuid.uuid4())
				db.execute(
					'INSERT INTO ports (id, port, state, service, version, note, host) VALUES (?, ?, ?, ?, ?, ?, ?)',
					(portid, p, state, service, version, "", hostid)
				)
			else:
				db.execute(
					'UPDATE ports SET service = ?, version = ? WHERE id = ?',
					(service, version, portcheck['id'])
				)
		
		
		db.execute(
			'UPDATE hosts SET portsq = ? WHERE id = ?',
			(portsq, hostid)
		)		


def parseMasscanFile(file, project, db):
	scan = ET.fromstring(file)
	for host in scan.findall('host'):
		ip = host.find('address').get('addr')

		hostCheck = db.execute(
			'SELECT * FROM hosts WHERE project = ? and ip = ?',
			(project, ip, )
		).fetchone()

		if hostCheck is None:
			hostid = str(uuid.uuid4())
			db.execute(
				'INSERT INTO hosts (id, ip, note, style, portsq, project) VALUES (?, ?, ?, ?, ?, ?)',
				(hostid, ip, "", "Default", 0, project)
			)
			portsq = 0
		else:
			hostid = hostCheck['id']
			portsq = int(hostCheck['portsq'])


		for port in host.find('ports').findall('port'):
			if port.find('state').get('state') != 'open':
				continue
			p = port.get('portid')

			portcheck = db.execute(
				'SELECT * FROM ports WHERE host = ? and port = ?', 
				(hostid, p)
			).fetchone()

			state = port.find('state').get('state')

			if portcheck is None:
				portsq = 1
				portid = str(uuid.uuid4())
				db.execute(
					'INSERT INTO ports (id, port, state, service, version, note, host) VALUES (?, ?, ?, ?, ?, ?, ?)',
					(portid, p, state, "", "", "", hostid)
				)		
		db.execute(
			'UPDATE hosts SET portsq = ? WHERE id = ?',
			(portsq, hostid)
		)			
		

def parseDomainFile(file, project, db):
	VALIDATEIP = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
	VALIDATEDOMAIN = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])(\:([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?$"
	ipre = re.compile(VALIDATEIP)
	domainre = re.compile(VALIDATEDOMAIN)
	for l in file:
		line = l.decode().strip()
		delimeter = line.rfind(':')
		domain = line[:delimeter]
		ip = line[delimeter + 1:]

		if not ipre.match(ip) or not domainre.match(domain):
			continue
		
		checkIfExists = db.execute(
			'SELECT * FROM domains WHERE project = ? and domain = ?', 
			(project, domain, )
		).fetchone()

		if checkIfExists is None:
			domainid = str(uuid.uuid4())
			ext = tldextract.extract(domain)
			lvl = ext[1] + "." + ext[2]
			db.execute(
				'INSERT INTO domains (id, domain, lvl, ip, note, style, project) VALUES (?, ?, ?, ?, ?, ?, ?)',
				(domainid, domain, lvl, ip, "", "Default", project)
			)	
		else:
			domainid = checkIfExists['id']
			db.execute(
				'UPDATE domains SET ip = ? WHERE id = ?',
				(ip, domainid)
			)
	

@bp.route('/update', methods = ['GET', 'POST'])
@login_required
def update():
	db = get_db()
	if request.method == 'GET':
		projectid = request.args.get('id')	
	else:
		projectid = request.form['id']		

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner =?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return render_template('info.html', username=session['username'], info='Not found')
									
	if request.method == 'GET':
		return render_template('main/update.html', username=session['username'], id=project['id'], name=project['name'])

	errors = []
	warnings = []
	nmapFile = request.files['nmapFile']
	nmapXML = nmapFile.stream.read()
	masscanFile = request.files['masscanFile']
	masscanXML = masscanFile.stream.read()
	domainFile = request.files['domainFile']


	if not nmapFile and not masscanFile and not domainFile:
		errors.append("Even one file is required")

	if not nmapFile:
		warnings.append("Nmap file was not uploaded")
	else:
		try:
			tree = ET.fromstring(nmapXML)
		except:
			errors.append("Nmap file is not a valid xml file")	

	if not masscanFile:
		warnings.append("Masscan file was not uploaded")
	else:
		try:
			tree = ET.fromstring(masscanXML)
		except:
			errors.append("Masscan file is not a valid xml file")

	if not domainFile:
		warnings.append("Domain file was not uploaded")	
			
	if errors:
		return render_template('main/update.html', username=session['username'], errors=errors, id=project['id'], name=project['name'])
		

	# Fill database
	try:
		if nmapFile:
			parseNmapFile(nmapXML, projectid, db)
		if masscanFile:
			parseMasscanFile(masscanXML, projectid, db)
		if domainFile:
			parseDomainFile(domainFile, projectid, db)
		db.commit()			
	except Exception as e:
		errors.append(str(e))
		return render_template('main/update.html', username=session['username'], errors=errors, id=project['id'], name=project['name'])
		
	success = "Project was successfully updated"
	return render_template('main/update.html', username=session['username'], success=success, warnings=warnings, id=project['id'], name=project['name'])

