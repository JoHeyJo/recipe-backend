import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Standard environment configuration"""
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False

class Development(Config):
    """Development environment configuration"""
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']
    
    SQLALCHEMY_ECHO = True
    DEBUG = True


class Production(Config):
    """Production environment configuration"""
    SQLALCHEMY_ECHO = True
    # DEBUG_TB_INTERCEPT_REDIRECTS = False # does this auto update flask app?
