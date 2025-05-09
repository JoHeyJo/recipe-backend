import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app

def access_app(app):
    app = app

class Config:
    """Standard environment configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

class DevelopmentConfig(Config):
    """Development environment configuration"""
    ENV = "development"
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_ECHO = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = True


class ProductionConfig(Config):
    """Production environment configuration"""
    def __init__(self, app):
        ENV = "production"
        JWT_SECRET_KEY = app.secret_key_jwt
        DEBUG_TB_INTERCEPT_REDIRECTS = False 
        # SECRET_KEY = app.secret_key_flask
