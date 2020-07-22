from flask import (
	Flask, Blueprint, flash, g, redirect, render_template, request, session, escape, Markup, Response, current_app
)
import subprocess
import tldextract
import sqlite3
import datetime
import os
import uuid
import requests
from threading import Thread

from app.auth import login_required
from app.helpers import taskClass
from app.db import get_db
from app.main import parseMasscanFile, parseNmapFile

from flask_crontab import Crontab

crontab = Crontab()

token = current_app.config['TOKEN']
channel = current_app.config['CHANNEL']
log_path = os.path.join(current_app.instance_path, 'logs', 'cron.log')
findomain_path = current_app.config["FINDOMAIN"]
amass_path = current_app.config["AMASS"]
database_path = current_app.config["DATABASE"]
masscan_path = current_app.config["MASSCAN"]
nmap_path = current_app.config["NMAP"]
proxy_url = current_app.config["PROXY_URL"]
proxy_port = current_app.config["PROXY_PORT"]
proxy_user = current_app.config["PROXY_USER"]
proxy_pass = current_app.config["PROXY_PASS"]


bp = Blueprint('cron', __name__, url_prefix='/cron')

@bp.route('/', methods = ['GET'])
@login_required
def cron():
	projectid = request.args.get('id')

	db = get_db()

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

	if 'search' not in request.args:
		search = '.*' 
	else:
		search = request.args.get('search').strip()

	if request.args.get('period') in ["1", "2", "3", "4", "5"]:
		period = request.args.get('period')	
	else:
		period = '%'

	if request.args.get('status') == "On":
		status = 1
		status_t = "On"
	elif request.args.get('status') == "Off":
		status = 0
		status_t = "Off"
	else:
		status = "%"
		status_t = "All"

	
	crons = db.execute(
		'SELECT * FROM crontab WHERE project = ? AND domain REGEXP ? AND status LIKE ? AND period LIKE ? ORDER BY rowid DESC LIMIT ? OFFSET ?',
		(projectid, search, status, period, limit, limit * (page - 1), )
	).fetchall()
	

	allcrons = db.execute(
		'SELECT * FROM crontab WHERE project = ? AND domain REGEXP ? AND status LIKE ? AND period LIKE ? ORDER BY rowid DESC',
		(projectid, search, status, period, )
	).fetchall()

	if len(allcrons) % limit == 0:
		pages = int(len(allcrons) / limit)
	else:
		pages = int(len(allcrons) / limit + 1)

	return render_template('cron/cron.html', username=session['username'], project=project, rows=crons, limit=limit, page=page, search=search, period=period, pages=pages, status=status_t)


def getdb():
	db = sqlite3.connect(
		database_path,
		detect_types=sqlite3.PARSE_DECLTYPES
	)
	db.row_factory = sqlite3.Row

	return db


def run(tasks):

	for task in tasks:
		
		thread = Thread(target=runsingle, args=(task['id'], task['project'], task['domain'], ))
		thread.start()

	return "1"


def runsingle(cronid, project, domain):

	text = "\[{}] Subdomain search was started".format(domain)
	postToTelegram(text)

	with open(log_path, 'a') as f:
		f.write("[{}][{}][{}] Subdomain search was started.\n".format(datetime.datetime.now(), cronid, domain))
	
	result = {}

	findomain_result = subprocess.run([findomain_path, '-q', '-i','-t', domain], stdout=subprocess.PIPE)
	findomain_domains = findomain_result.stdout.decode('utf-8').split('\n')

	amass_result = subprocess.run([amass_path, 'enum', '-active', '-ipv4', '-d', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	amass_domains = amass_result.stdout.decode('utf-8').split('\n')

	for d in findomain_domains:
		if d == '':
			continue
		t = d.split(',')
		result[t[0]] = t[1] 

	for d in amass_domains:
		if d == '':
			continue
		t = d.split(' ')
		result[t[0]] = t[1].split(',')[0] 	
	
	db = getdb()

	newDomains = []
	for key in result:
		if addDomain(project, key, result[key], db) == "1":
			newDomains.append(key)	

	db.commit()
	
	if len(newDomains) != 0:
		text = "\[{}] New domains were found:\n".format(domain)
		for d in newDomains:
			text += "{}\n".format(d)
		postToTelegram(text)	

	text = "\[{}] Subdomain search was finished".format(domain)
	postToTelegram(text)
	
	with open(log_path, 'a') as f:
		f.write("[{}][{}][{}] Subdomain search was finished.\n".format(datetime.datetime.now(), cronid, domain))
	
	db.close()

	with open(log_path, 'a') as f:
		f.write("[{}][{}][{}] DB was closed.\n".format(datetime.datetime.now(), cronid, domain))

	return "1"


def addDomain(project, domain, ip, db):
	checkIfExists = db.execute(
		'SELECT * FROM domains WHERE project = ? and domain = ?', 
		(project, domain, )
	).fetchone()

	checkIfHostExists = db.execute(
		'SELECT * FROM hosts WHERE project = ? and ip = ?', 
		(project, ip, )
	).fetchone()

	if checkIfHostExists is None:
		hostid = str(uuid.uuid4())
		db.execute(
			'INSERT INTO hosts (id, ip, note, style, portsq, project) VALUES (?, ?, ?, ?, ?, ?)',
			(hostid, ip, "", "New", 0, project)
		)

	if checkIfExists is None:
		domainid = str(uuid.uuid4())
		ext = tldextract.extract(domain)
		lvl = ext[1] + "." + ext[2]
		db.execute(
			'INSERT INTO domains (id, domain, lvl, ip, note, style, project) VALUES (?, ?, ?, ?, ?, ?, ?)',
			(domainid, domain, lvl, ip, "", "New", project)
		)
		return "1"	
	else:
		domainid = checkIfExists['id']
		db.execute(
			'UPDATE domains SET ip = ? WHERE id = ?',
			(ip, domainid)
		)
		return "0"	



@crontab.job(minute="0", hour="*/2")
def cron2hours():

	db = getdb()

	crons = db.execute(
		'SELECT id, domain, project FROM crontab WHERE status = "1" AND period = "2"'
	).fetchall()

	db.close()

	run(crons)

	return "1"	

@crontab.job(minute="0", hour="*/5")
def cron5hours():
	db = getdb()
	
	crons = db.execute(
		'SELECT id, domain, project FROM crontab WHERE status = "1" AND period = "3"'
	).fetchall()

	db.close()
	
	run(crons)
	
	return "1"	

@crontab.job(minute="0", hour="10")
def crondaily():
	db = getdb()
	
	crons = db.execute(
		'SELECT id, domain, project FROM crontab WHERE status = "1" AND period = "4"'
	).fetchall()

	db.close()

	run(crons)
	
	return "1"	

@crontab.job(minute="0", hour="10", day_of_week="1")
def cronweekly():
	db = getdb()
	
	crons = db.execute(
		'SELECT id, domain, project FROM crontab WHERE status = "1" AND period = "5"'
	).fetchall()

	db.close()

	run(crons)
	
	return "1"		


def postToTelegram(text):
	if proxy_url.strip() == "" or proxy_port.strip() == "":
		proxies = {}
	elif proxy_user == "" or proxy_pass == "":
		proxies = {'http': 'socks5://{}:{}'.format(proxy_url, proxy_port), 'https' : 'socks5://{}:{}'.format(proxy_url, proxy_port) }
	else:
		proxies = {'http': 'socks5://{}:{}@{}:{}'.format(proxy_user, proxy_pass, proxy_url, proxy_port), 'https' : 'socks5://{}:{}@{}:{}'.format(proxy_user, proxy_pass, proxy_url, proxy_port) }
	

	resp = requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&parse_mode=Markdown".format(token, channel, text), proxies=proxies)
	status = resp.status_code
	return "1"	


def runMasscan(projectid, projectname, ips, t):

	postToTelegram("\[{}]\[Type={}] Masscan scan was started.".format(projectname, t))
	output = "/tmp/masscan_{}".format(str(uuid.uuid4()))

	out = subprocess.run([masscan_path, '-p', '1-65535','--rate', '2000', '-oX', output, ips], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	db = getdb()
	
	try:
		with open(output, 'r') as content_file:
			masscanXML = content_file.read()
			if masscanXML == "":
				postToTelegram("\[{}]\[Type={}] Masscan scan was finished. Nothing was found.".format(projectname, t))
				return "1"
			parseMasscanFile(masscanXML, projectid, db)
			db.commit()
	except Exception as e:
		with open(log_path, 'a') as log:
			log.write("[{}][{}] Masscan scan was not finished correctly. {}\n".format(datetime.datetime.now(), projectname, str(e)))
		postToTelegram("\[{}]\[Type={}] Masscan scan was not finished correctly.".format(projectname, t))
		return "1"
	finally:
		db.close()
		os.remove(output)	

	
	postToTelegram("\[{}]\[Type={}] Masscan scan was finished.".format(projectname, t))



def runNmap(projectid, projectname, ips, t):

	postToTelegram("\[{}]\[Type={}] Nmap scan was started.".format(projectname, t))
	
	inp = "/tmp/nmap_{}".format(str(uuid.uuid4()))
	with open(inp, 'a') as f:
		f.write("\n".join(map(lambda x: x, ips)))

	output = "/tmp/nmap_{}".format(str(uuid.uuid4()))
	out = subprocess.run([nmap_path, '--top-ports', '10000', '-iL', inp, '-sV', '-Pn', '--min-rate', "300", '--max-retries', '2', '-oX', output], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	db = getdb()
	try:
		with open(output, 'r') as content_file:
			nmapXML = content_file.read()
			if nmapXML == "":
				postToTelegram("\[{}]\[Type={}] Nmap scan was finished. Nothing was found.".format(projectname, t))
				return "1"
			parseNmapFile(nmapXML, projectid, db)
			db.commit()
	except Exception as e:
		with open(log_path, 'a') as log:
			log.write("[{}][{}] Nmap scan was not finished correctly. {}\n".format(datetime.datetime.now(), projectname, str(e)))
		postToTelegram("\[{}]\[Type={}] parseNmapFile scan was not finished correctly.".format(projectname, t))
		return "1"
	finally:
		db.close()
		os.remove(inp)
		os.remove(output)	

	
	postToTelegram("\[{}]\[Type={}] Nmap scan was finished.".format(projectname, t))
