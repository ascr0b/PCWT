from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)

from werkzeug.security import check_password_hash, generate_password_hash
import xml.etree.ElementTree as ET
import uuid
import re

from app.auth import login_required
from app.db import get_db


bp = Blueprint('main', __name__)

@bp.route('/', methods = ['GET'])
@login_required
def index():
	db = get_db()
	projects = db.execute(
		'SELECT id, name FROM projects WHERE owner = ?', (session['username'], )
	).fetchall()
	return render_template('main/main.html', username=session['username'], rows=projects)

@bp.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
	if request.method == 'GET':
		return render_template('main/profile.html', username=session['username'])
	db = get_db()
	errors = []
	oldpwd = request.form['oldpwd']
	pwd = request.form['pwd']
	pwdconfirm = request.form['pwdconfirm']

	user = db.execute(
		'SELECT password FROM users WHERE username = ?',
		(session['username'], )
	).fetchone()

	if not oldpwd or not pwd or not pwdconfirm:
		errors.append('All fields must be filled')

	if not check_password_hash(user['password'], oldpwd):
		errors.append('Incorrect current password')

	if pwd != pwdconfirm:
		errors.append('New passwords do not match')

	if errors:
		return render_template('main/profile.html', username=session['username'], errors=errors)

	db.execute(
		'UPDATE users SET password = ? WHERE username = ?',
		(generate_password_hash(pwd), session['username'], )
	)
	db.commit()

	return render_template('main/profile.html', username=session['username'], success=True)	


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
			service = port.find('service').get('name')
			version = port.find('service').get('product')
			if port.find('service').get('version'):
				version += " " + port.find('service').get('version')

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
			db.execute(
				'INSERT INTO domains (id, domain, ip, note, style, project) VALUES (?, ?, ?, ?, ?, ?)',
				(domainid, domain, ip, "", "Default", project)
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
