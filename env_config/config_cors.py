import os
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def configure_cors(app):
    """Dynamically handle configuration of CORS based on environment"""
    if app.config['ENV'] == 'production':
        CORS(app,
             origins=["https://slingitdrinks.com"],
             supports_credentials=True,
             methods=["GET", "POST", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization"])
    else:
        CORS(app, resources={r"/*": {"origins": {os.environ["CLIENT_URL"]}}})
