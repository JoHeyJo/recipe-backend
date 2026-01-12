import os
from dotenv import load_dotenv

load_dotenv()

def load_config(app):
    """Loads keys into current app configurations from .env"""
    app.config["CLIENT_ORIGIN_URL"] = os.environ("CLIENT_URL")
    app.config["AWS_REGION"] = os.environ("AWS_REGION")
    app.config["SES_FROM_EMAIL"] = os.environ("SES_FROM_EMAIL")
    app.config["FRONTEND_RESET_URL"] = os.environ("FRONTEND_RESET_URL")
