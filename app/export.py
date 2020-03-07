from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, escape, Markup, Response
)

from app.auth import login_required
from app.db import get_db

bp = Blueprint('export', __name__, url_prefix='/export')

@bp.route('/', methods = ['GET'])
@login_required
def export():
	projectid = request.args.get('id')

	db = get_db()

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return render_template('info.html', username=session['username'], info='Not found')

	return render_template('export/main.html', username = session['username'], projectid=projectid)


@bp.route('/exportIPwithoutScan', methods = ['GET'])
@login_required
def exportIPwithoutScan():
	db = get_db()
	projectid = request.args.get('id')

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	hosts = db.execute(
		'SELECT DISTINCT ip FROM domains WHERE project = ? AND ip NOT IN \
		(SELECT ip FROM hosts where project = ?)',
		(projectid, projectid, )
	).fetchall()
	
	return Response("\n".join(map(lambda x: x['ip'], hosts)), mimetype='plain/txt', headers={"Content-Disposition": "attachment; filename*=UTF-8''exportIPwithoutScan.txt"})	


@bp.route('/exportIP', methods = ['GET'])
@login_required
def exportIP():
	db = get_db()
	projectid = request.args.get('id')

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	hosts = db.execute(
		'SELECT ip FROM hosts WHERE project = ?',
		(projectid, )
	).fetchall()

	return Response("\n".join(map(lambda x: x['ip'], hosts)), mimetype='plain/txt', headers={"Content-Disposition": "attachment; filename*=UTF-8''exportIP.txt"})	

@bp.route('/exportDomainIPByIP', methods = ['GET'])
@login_required
def exportDomainIPbyIP():
	db = get_db()
	projectid = request.args.get('id')

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	domains = db.execute(
		'SELECT domain || ":" || ip as d FROM domains WHERE project = ? ORDER BY ip, lvl, domain',
		(projectid, )
	).fetchall()

	return Response("\n".join(map(lambda x: x['d'], domains)), mimetype='plain/txt', headers={"Content-Disposition": "attachment; filename*=UTF-8''exportDomainIPByIP.txt"})


@bp.route('/exportDomainIPByDomain', methods = ['GET'])
@login_required
def exportDomainIPbyDomain():
	db = get_db()
	projectid = request.args.get('id')

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')


	domains = db.execute(
		'SELECT domain || ":" || ip as d FROM domains WHERE project = ? ORDER BY lvl, domain, ip',
		(projectid,)
	).fetchall()

	return Response("\n".join(map(lambda x: x['d'], domains)), mimetype='plain/txt', headers={"Content-Disposition": "attachment; filename*=UTF-8''exportDomainIPByDomain.txt"})



@bp.route('/exportDomainByIP', methods = ['GET'])
@login_required
def exportDomainbyIP():
	db = get_db()
	projectid = request.args.get('id')

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	domains = db.execute(
		'SELECT domain as d FROM domains WHERE project = ? ORDER BY ip, lvl, domain',
		(projectid,)
	).fetchall()

	return Response("\n".join(map(lambda x: x['d'], domains)), mimetype='plain/txt', headers={"Content-Disposition": "attachment; filename*=UTF-8''exportDomainByIP.txt"})

@bp.route('/exportDomainByDomain', methods = ['GET'])
@login_required
def exportDomainbyDomain():
	db = get_db()
	projectid = request.args.get('id')

	project = db.execute(
		'SELECT id, name FROM projects WHERE id = ? and owner = ?',
		(projectid, session['username'], )
	).fetchone()

	if not project:
		return Response(json.dumps({"status": "not found"}), mimetype='application/json')

	domains = db.execute(
		'SELECT domain as d FROM domains WHERE project = ? ORDER BY lvl, domain, ip',
		(projectid,)
	).fetchall()

	return Response("\n".join(map(lambda x: x['d'], domains)), mimetype='plain/txt', headers={"Content-Disposition": "attachment; filename*=UTF-8''exportDomainByDomain.txt"})	