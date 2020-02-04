from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, escape, Markup, Response
)
from collections import OrderedDict
import markdown
import bleach
from bleach_whitelist import markdown_tags, markdown_attrs
import json
import re
from app.auth import login_required
from app.db import get_db
from app.main import parseNmapFile
from app.helpers import *

bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/hosts', methods = ['GET'])
@login_required
def hosts():
	db = get_db()
	scan = projectClass()
	projectid = request.args.get('id')
	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return render_template('info.html', username=session['username'], info='Not found')

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

	if request.args.get('type') in ['Hacked', 'Checked', 'Suspicious', 'Default']:
		style = request.args.get('type')	
	else:
		style = '%'

	if 'search' not in request.args:
		search = '.*' 
	else:
		search = request.args.get('search')
	
	if request.args.get('noports') == 'False':
		noports_t = 'False'
		noports = 1	
	else:
		noports_t = 'True'
		noports = '%'

		


	scan.id = escape(project['id'])
	scan.name = escape(project['name'])
	scan.hosts = []	

	hosts = db.execute(
		'SELECT id, ip, note, style FROM hosts WHERE project = ? AND (ip REGEXP ? OR note REGEXP ?) AND style LIKE ? AND portsq LIKE ? LIMIT ? OFFSET ?',
		(projectid, search, search, style, noports, limit, limit * (page - 1), )
	).fetchall()

	for host in hosts:
		hostObj = hostClass()
		hostObj.id = escape(host['id'])
		hostObj.ip = escape(host['ip'])
		hostObj.style = host['style']
		if host['note']:
			hostObj.note = Markup(bleach.clean(markdown.markdown(host['note']), markdown_tags, markdown_attrs))
		hostObj.ports = []
		ports = db.execute(
			'SELECT id, port, state, service, version, note FROM ports WHERE host = ?',
			(hostObj.id, )
		).fetchall()

		#if len(ports) == 0:
		#	continue
			
		for port in ports:
			portObj = portClass()
			portObj.id = escape(port['id'])
			portObj.port = escape(port['port'])
			portObj.state = escape(port['state'])
			portObj.service = escape(port['service'])
			if port['version']:
				portObj.version = port['version']
			if port['note']:
				portObj.note = Markup(bleach.clean(markdown.markdown(port['note']),markdown_tags, markdown_attrs))
			hostObj.ports.append(portObj)
			del portObj
		scan.hosts.append(hostObj)
		del hostObj

	allhosts = db.execute(
		'SELECT id, ip, note, style FROM hosts WHERE project = ? AND (ip REGEXP ? OR note REGEXP ?) AND style LIKE ? AND portsq LIKE ?',
		(projectid, search, search, style, noports )
	).fetchall()

	if len(allhosts) % limit == 0:
		pages = int(len(allhosts) / limit)
	else:
		pages = int(len(allhosts) / limit + 1)

	return render_template('project/hosts.html', username=session['username'], scan=scan, limit=limit, pages=pages, page=page, search=search, type=style, noports=noports_t)

	


@bp.route('/ports', methods = ['GET'])
@login_required
def ports():
	db = get_db()
	scan = portDashboardClass()
	projectid = escape(request.args.get('id'))

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner =?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return render_template('info.html', username=session['username'], info='Not found')

	scan.id = escape(project['id'])
	scan.name = escape(project['name'])

	hosts = db.execute(
		'SELECT id, ip FROM hosts WHERE project = ?', (projectid, )
	).fetchall()
	ports = {}
	scan.ports = []

	for host in hosts:
		allports = db.execute(
			'SELECT port FROM ports WHERE host = ?', (host['id'], )
		).fetchall()
		for port in allports:
			if port['port'] not in ports:
				ports[port['port']] = [1, []]
			else:
				ports[port['port']][0] += 1
			ports[port['port']][1].append(host['ip'])	

	port_asc = OrderedDict(sorted(ports.items(), key=lambda kv: kv[1][0], reverse=True))

	for x in port_asc:
		portMini = portMiniClass()
		portMini.port = x
		portMini.amount = ports[x][0]
		portMini.hosts = ports[x][1]
		scan.ports.append(portMini)

	return render_template("project/ports.html", username=session['username'], scan=scan)


@bp.route('/domains', methods = ['GET'])
@login_required
def domains():
	db = get_db()
	projectid = request.args.get('id')
	scan = domainsDashboardClass()


	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner =?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return render_template('info.html', username=session['username'], info='Not found')


	if 'search' not in request.args:
		search = '.*' 
	else:
		search = request.args.get('search')
	#searchsql = '%' + search + '%'	

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

	if request.args.get('type') in ['Hacked', 'Checked', 'Suspicious', 'Default']:
		style = request.args.get('type')	
	else:
		style = '%'	
							


	scan.id = escape(project['id'])
	scan.name = escape(project['name'])
	scan.domains = []


	domainsList = db.execute(
		'SELECT * FROM domains WHERE project = ? and style LIKE ? and (ip REGEXP ? or note REGEXP ? or domain REGEXP ?) ORDER BY ip LIMIT ? OFFSET ?', 
		(projectid, style, search, search, search, limit, limit * (page - 1), )
	).fetchall()

	for d in domainsList:
		domain = domainClass()
		domain.id = escape(d['id'])
		domain.domain = escape(d['domain'])
		domain.ip = escape(d['ip'])
		domain.style = escape(d['style'])
		if d['note']:
			domain.note = Markup(bleach.clean(markdown.markdown(d['note']), markdown_tags, markdown_attrs))
		scan.domains.append(domain)
		del domain 

	alldomains = db.execute(
		'SELECT id FROM domains WHERE project = ? and style LIKE ? and (ip REGEXP ? or note REGEXP ? or domain REGEXP ?)',
		(projectid, style, search, search, search, )
	).fetchall()
	
	if len(alldomains) % limit == 0:
		pages = int(len(alldomains) / limit)
	else:
		pages = int(len(alldomains) / limit + 1)
	
	return render_template('project/domains.html', username=session['username'], scan=scan, limit=limit, page=page, search=search, type=style, pages=pages)




