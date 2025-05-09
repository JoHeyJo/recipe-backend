from environment_config import DevelopmentConfig, ProductionConfig, os

def set_environment(app):
	"""On application load environment is set based on server software"""
	if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
		app.config.from_object(ProductionConfig)
		ProductionConfig.config_app(app=app)
	else:
		app.config.from_object(DevelopmentConfig)

