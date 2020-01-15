import os

from flask import Flask

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	#csrf = CSRFProtect(app)
	app.config.from_mapping(
		SECRET_KEY='change it',
		DATABASE=os.path.join(app.instance_path, 'scans.sqlite')
	)

	if test_config is None:
        # load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
        # load the test config if passed in
		app.config.from_mapping(test_config)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

    # a simple page that says hello
	#@app.route('/')
	#def hello():
	#	return 'Hello, World!'

	from . import db
	db.init_app(app)

	from . import auth
	app.register_blueprint(auth.bp)

	from . import project
	app.register_blueprint(project.bp)

	from . import api
	app.register_blueprint(api.bp)

	from . import main 
	app.register_blueprint(main.bp)
	app.add_url_rule('/', endpoint='index')

	return app
