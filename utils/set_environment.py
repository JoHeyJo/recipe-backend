from environment_config import Development, Production, os


def set_environment(app):
	"""On application load environment is set based on server software"""
	if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
		app.config.from_object(Production)
	else:
		app.config.from_object(Development)
