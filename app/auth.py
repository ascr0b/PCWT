import functools, random, hashlib

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
	if 'username' in session:
		return redirect('/')

	if request.method == 'POST':
		username = request.form['username'].lower()
		password = request.form['password']
		db = get_db()
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'
		elif db.execute(
			'SELECT id from users WHERE username = ?', (username,)
		).fetchone() is not None:
			error = 'User already exists.'

		if error is None:
			db.execute(
				'INSERT INTO users (username, password) VALUES (?, ?)',
				(username, generate_password_hash(password))
			)
			db.commit()
			return redirect('/auth/signin')
		else:
			return render_template('auth/signup.html', info=error)

	elif request.method == 'GET':
		return render_template('auth/signup.html')				

@bp.route('/signin', methods=['GET', 'POST'])
def signin():
	if 'username' in session:
		return redirect('/')

	if request.method == 'POST':
		username = request.form['username'].lower()
		password = request.form['password']
		db = get_db()
		error = None
		user = db.execute(
			'SELECT * FROM users WHERE username = ?', 
			(username, )
		).fetchone()

		if (user is None) or not check_password_hash(user['password'], password):
			error = 'Invalid username or password'
			return render_template('auth/signin.html', info = error)
		else:
			session['username'] = user['username']
			return redirect('/')
	elif request.method == 'GET':
		return render_template('auth/signin.html')		

@bp.route('/logout', methods = ['GET'])
def logout():
	session.clear()	
	return redirect('/auth/signin')	

@bp.before_app_request
def load_looged_in_user():
	username = session.get('username')

	if username is None:
		g.user = None
	else:
		g.user = get_db().execute(
			'SELECT * FROM users WHERE username = ?', (username, )
		).fetchone()

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect('/auth/signin')
		return view(**kwargs)
	return wrapped_view				