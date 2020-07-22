# PCWT

A web application that makes it easy to run your pentest and bug bounty projects.

## Description

The app provides a convenient web interface for working with various types of files that are used during the pentest, automate port scan and subdomain search.

### Main page

![Main page](https://raw.githubusercontent.com/ascr0b/PCWT/master/images/mainpage.png =250x)

### Project settings

![Settings](https://raw.githubusercontent.com/ascr0b/PCWT/master/images/settings.png =250x)


### Domains dashboard

![Domains](https://raw.githubusercontent.com/ascr0b/PCWT/master/images/domains.png =250x)

### Port scan

You can scan ports using nmap or masscan. The nmap is started with the following arguments:

```
nmap --top-ports 10000 -sV -Pn --min-rate 300 --max-retries 2 [ip]
```

The masscan is started with the following arguments:

```
masscan -p 1-65535 --rate 2000
```

### Subdomain search

[Amass](https://github.com/OWASP/Amass) and [findomain](https://github.com/Edu4rdSHL/findomain) are used to find subdomains.


### Features

* Leave notes to host, port or domain.
* Mark host or domain with tags.
* Search by any field related with host, port or domain (tags and notes are included). Regexp is available.
* Different types of sorting ara available on almost all dashboards.
* Run port scan for all hosts, hosts without port scan or custom list.
* Create tasks for subdomains search (every 2 hours, every 5 hours, every day or every week). You can also disable and enable them on demand using `Subdomain tasks` dashboard.
* Different types of export are available.
* Notifications about the start and end of the scan, as well as about new found domains can be sent to Telegram. Update the `config.py` with your chat id and token.

## Install from sources

NOTE: Change the paths for amass, findomain, nmap and masscan in `config.py` before running commands.

```
apt install python3 python-venv python3-pip
git clone https://github.com/ascr0b/PCWT
cd PCWT

python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt

flask init-db
flask crontab add

export FLASK_APP=app
flask run
```

The app is available at http://127.0.0.1:5000

