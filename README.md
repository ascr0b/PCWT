# PCWT

A web application that makes it easy to run your pentest and bug bounty projects.

## Description

The app provides a convenient web interface for working with various types of files that are used during the pentest. 

## Install from sources

```
apt install python3 python3-venv python3-pip
git clone https://github.com/ascr0b/PCWT

python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
flask init-db

export FLASK_APP=app
flask run
```

The app is available at http://127.0.0.1:5000

## Install via Docker

```
git clone https://github.com/ascr0b/PCWT
docker build . -t pcwt
docker run -d -p 9000:5000 pcwt
```

The app is available at http://127.0.0.1:9000
