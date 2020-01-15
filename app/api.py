from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, escape, Markup, Response
)
import json
import markdown
import bleach
from bleach_whitelist import markdown_tags, markdown_attrs
import uuid
import re

from app.auth import login_required
from app.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')


###########################################
@bp.route('/getHostNote', methods=['POST'])
@login_required
def getHostNote():
	db = get_db()
	hostid = request.get_json()['hostid']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN hosts ON projects.id = hosts.project WHERE hosts.id = ?',
		(hostid, )
	).fetchone()


	if not check_access or not hostid:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	note = db.execute(
		'SELECT note FROM hosts WHERE id = ?',
		(hostid,)
	).fetchone()

	return Response(json.dumps({'note' : note['note']}), mimetype='application/json')


@bp.route('/updateHostNote', methods=['POST'])
@login_required
def updateHostNote():
	db = get_db()
	hostid = request.get_json()['hostid']
	note = request.get_json()['note']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN hosts ON projects.id = hosts.project WHERE hosts.id = ?',
		(hostid, )
	).fetchone()

	if not check_access or not hostid or not note:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'UPDATE hosts SET note = ? WHERE id = ?',
		(note.strip(), hostid, )
	)
	db.commit()

	return Response(json.dumps({"note": Markup(bleach.clean(markdown.markdown(note), markdown_tags, markdown_attrs)) }), mimetype='application/json')


@bp.route('/updateHostStyle', methods=['POST'])
@login_required
def updateHostStyle():
	db = get_db()
	hostid = request.get_json()['hostid']
	styleType = request.get_json()['type']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN hosts ON projects.id = hosts.project WHERE hosts.id = ?',
		(hostid, )
	).fetchone()

	if not check_access or not hostid or not styleType:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	if styleType in ["Checked", "Hacked", "Suspicious", "Default"]:
		style = styleType
	else:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'UPDATE hosts SET style = ? WHERE id = ?',
		(style, hostid, )
	)	
	db.commit()
	return Response(json.dumps({"style": style}), mimetype='application/json')	


@bp.route('/deleteHost', methods=['POST'])
@login_required
def deleteHost():
	db = get_db()
	hostid = request.get_json()['hostid']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN hosts ON projects.id = hosts.project WHERE hosts.id = ?',
		(hostid, )
	).fetchone()

	if not check_access or not hostid:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'DELETE FROM ports WHERE host = ?',
		(hostid, )
	)
	db.execute(
		'DELETE FROM hosts WHERE id = ?',
		(hostid, )
	)
	db.commit()
	return Response(json.dumps({"status": "success"}), mimetype='application/json')		

###########################################

###########################################
@bp.route('/getPortNote', methods=['POST'])
@login_required
def getPortNote():
	db = get_db()
	portid = request.get_json()['portid']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN hosts ON projects.id = hosts.project INNER JOIN ports ON hosts.id = ports.host WHERE ports.id = ?',
		(portid, )
	).fetchone()

	if not check_access or not portid:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	note = db.execute(
		'SELECT note FROM ports WHERE id = ?',
		(portid, )
	).fetchone()

	return Response(json.dumps({'note' : note['note']}), mimetype='application/json')


@bp.route('/updatePortNote', methods=['POST'])
@login_required
def updatePortNote():
	db = get_db()
	portid = request.get_json()['portid']
	note = request.get_json()['note']
	
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN hosts ON projects.id = hosts.project INNER JOIN ports ON hosts.id = ports.host WHERE ports.id = ?',
		(portid, )
	).fetchone()

	if not check_access or not portid or not note:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'UPDATE ports SET note = ? WHERE id = ?',
		(note.strip(), portid)
	)
	db.commit()

	return Response(json.dumps({"note": Markup(bleach.clean(markdown.markdown(note), markdown_tags, markdown_attrs)) }), mimetype='application/json')

###########################################
		
###########################################
@bp.route('/getDomainNote', methods=['POST'])
@login_required
def getDomainNote():
	db = get_db()
	domainid = request.get_json()['domainid']

	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN domains ON projects.id = domains.project WHERE domains.id = ?',
		(domainid, )
	).fetchone()

	if not check_access or not domainid :
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json') 

	note = db.execute(
		'SELECT note FROM domains WHERE id = ?',
		(domainid, )
	).fetchone()

	return Response(json.dumps({'note' : note['note']}), mimetype='application/json')	

@bp.route('/updateDomainNote', methods=['POST'])
@login_required
def updateDomainNote():
	db = get_db()
	domainid = request.get_json()['domainid']
	note = request.get_json()['note']

	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN domains ON projects.id = domains.project WHERE domains.id = ?',
		(domainid, )
	).fetchone()

	if not check_access or not domainid :
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'UPDATE domains SET note = ? WHERE id = ?',
		(note.strip(), domainid, )
	)

	db.commit()

	return Response(json.dumps({"note": Markup(bleach.clean(markdown.markdown(note), markdown_tags, markdown_attrs)) }), mimetype='application/json')


@bp.route('/updateDomainStyle', methods=['POST'])
@login_required
def updateDomaintStyle():
	db = get_db()
	domainid = request.get_json()['domainid']
	styleType = request.get_json()['type']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN domains ON projects.id = domains.project WHERE domains.id = ?',
		(domainid, )
	).fetchone()

	if not check_access or not domainid or not styleType:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if	check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	if styleType in ["Checked", "Hacked", "Suspicious", "Default"]:
		style = styleType
	else:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'UPDATE domains SET style = ? WHERE id = ?',
		(style, domainid, )
	)	
	db.commit()
	return Response(json.dumps({"style": style}), mimetype='application/json')


@bp.route('/deleteDomain', methods=['POST'])
@login_required
def deleteDomain():
	db = get_db()
	domainid = request.get_json()['domainid']
	check_access = db.execute(
		'SELECT projects.owner FROM projects INNER JOIN domains ON projects.id = domains.project WHERE domains.id = ?',
		(domainid, )
	).fetchone()

	if not check_access or not domainid:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')
	if check_access['owner'] != session['username']:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	db.execute(
		'DELETE FROM domains WHERE id = ?',
		(domainid, )
	)

	db.commit()
	return Response(json.dumps({"status": "success"}), mimetype='application/json')

###########################################

###########################################
@bp.route('/addHost', methods=['POST'])
@login_required
def addHost():
	db = get_db()
	project = request.get_json()['project']
	ip = request.get_json()['ip']
	ports = request.get_json()['ports']
	errors = []

	check_access = db.execute(
		'SELECT * FROM projects WHERE owner = ? and id = ?',
		(session['username'], project, )
	).fetchone()

	if not check_access or not ip or not ports or not project:
		return Response(json.dumps({"status" : "not found"}), mimetype='application/json')

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

	for port in ports:
		p = port['port']

		portcheck = db.execute(
			'SELECT * FROM ports WHERE host = ? and port = ?', 
			(hostid, p, )
		).fetchone()	

		state = "open"
		service = port['service']
		version = port['product']	

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
	
	db.commit()

	return Response(json.dumps({"status": "success"}), mimetype='application/json')		


@bp.route('/addDomain', methods=['POST'])
@login_required
def addDomain():
	db = get_db()
	project = request.get_json()['project']
	domain = request.get_json()['domain']
	ip = request.get_json()['ip']

	check_access = db.execute(
		'SELECT * FROM projects WHERE owner = ? and id = ?',
		(session['username'], project, )
	).fetchone()

	if not check_access or not domain or not ip:
		return Response(json.dumps({"status" : "not found"}), mimetype='application/json')

	VALIDATEIP = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
	VALIDATEDOMAIN = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])(\:([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?$"
	ipre = re.compile(VALIDATEIP)
	domainre = re.compile(VALIDATEDOMAIN)	

	if not ipre.match(ip) or not domainre.match(domain):
		return Response(json.dumps({"status" : "Validation error"}), mimetype='application/json')

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

	db.commit()
	return Response(json.dumps({"status": "success"}), mimetype='application/json')			