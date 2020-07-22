import os

from flask import Flask

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)

	try:
		os.makedirs(app.instance_path)
		os.makedirs(os.path.join(app.instance_path, 'logs'))
	except OSError:
		pass

	if test_config is None:
        # load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
		app.config.update(
			DATABASE=os.path.join(app.instance_path, 'scans.sqlite')
		)
		app.app_context().push()
	else:
        # load the test config if passed in
		app.config.from_mapping(test_config)	
	

	from . import db
	db.init_app(app)

	from . import auth
	app.register_blueprint(auth.bp)

	from . import project
	app.register_blueprint(project.bp)

	from . import export
	app.register_blueprint(export.bp)

	from . import cron
	app.register_blueprint(cron.bp)

	from app.cron import crontab
	crontab.init_app(app)

	from . import api
	app.register_blueprint(api.bp)

	from . import main 
	app.register_blueprint(main.bp)
	app.add_url_rule('/', endpoint='index')

	return app
