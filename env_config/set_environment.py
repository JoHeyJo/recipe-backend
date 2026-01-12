from environment_config import DevelopmentConfig, ProductionConfig, os
from SDKs.parameter_store_api import fetch_secrets
from utils.functions import highlight

def set_environment(app):
	"""On application load environment is set based on server software"""
	if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
		fetch_secrets(app=app)
		app.config.from_object(ProductionConfig)
	else:
		app.config.from_object(DevelopmentConfig)


# def get_config(key: str, required: bool = False, default=None):
#     value = app.config.get(key) or os.environ.get(key) or default

#     if required and value is None:
#         raise RuntimeError(f"Missing required config: {key}")

#     return value
