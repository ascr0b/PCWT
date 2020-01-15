# Install

```
apt install python3 python-venv python3-pip
git clone https://github.com/ascr0b/PCWT
python3 -m venv env
pip3 install -r requirements.txt

flask init-db
export FLASK_APP=app
flask run
```

Now you can access the app at http://127.0.0.1:5000. By default user `admin:admin` is created.
