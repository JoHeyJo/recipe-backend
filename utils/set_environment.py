from environment_config import DevelopmentConfig, ProductionConfig, os
from SDKs.parameter_store_api import fetch_secrets
from utils.functions import highlight

def set_environment(app):
	"""On application load environment is set based on server software"""
	if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
		fetch_secrets(app=app)
		app.config.from_object(ProductionConfig)
	else:
		fetch_secrets(app=app)
		app.config.from_object(DevelopmentConfig)

