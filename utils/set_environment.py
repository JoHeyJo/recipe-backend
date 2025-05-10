from environment_config import DevelopmentConfig, ProductionConfig, os
from SDKs.parameter_store_api import fetch_flask_secret, fetch_jwt_secret

def set_environment(app):
	"""On application load environment is set based on server software"""
	if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
		fetch_jwt_secret(app=app)
		fetch_flask_secret(app=app)
		app.config.from_object(ProductionConfig)
		ProductionConfig.config_app(app=app)
	else:
		app.config.from_object(DevelopmentConfig)

