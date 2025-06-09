import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Standard environment configuration"""
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    JWT_VERIFY_SUB = False


class DevelopmentConfig(Config):
    """Development environment configuration"""
    ENV = "development"
    SECRET_KEY = os.environ['SECRET_KEY']
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']
    SQLALCHEMY_ECHO = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = True


class ProductionConfig(Config):
    """Production environment configuration"""
    ENV = "production"
    DEBUG_TB_INTERCEPT_REDIRECTS = False
