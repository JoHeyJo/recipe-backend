import os
from dotenv import load_dotenv
from environment_config import DevelopmentConfig, ProductionConfig, os
from SDKs.parameter_store_api import fetch_secrets
from utils.functions import highlight

load_dotenv()

environment = os.getenv("ENV", "production")

def set_environment_config(app):
	"""On application load environment configuration is set for production or development"""
	if environment == "production":
		app.config.from_object(ProductionConfig)
		fetch_secrets(app=app)
	else:
		app.config.from_object(DevelopmentConfig)