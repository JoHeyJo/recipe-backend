import os
from datetime import timedelta
from dotenv import load_dotenv
from utils.functions import highlight

load_dotenv()


class Config:
    """Standard environment configuration"""
    highlight(os.environ,"#")
    try:
        SECRET_KEY = os.environ['SECRET_KEY']
    except KeyError:
        raise RuntimeError(
            "SECRET_KEY environment variable is required but not set.")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    JWT_VERIFY_SUB = False


class DevelopmentConfig(Config):
    """Development environment configuration"""
    ENV = "development"
    try:
        JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
    except KeyError:
        raise RuntimeError(
            "JWT_SECRET_KEY environment variable is required but not set.")
    try:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']
    except KeyError:
        raise RuntimeError(
            "DATABASE_URI environment variable is required but not set.")
    SQLALCHEMY_ECHO = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = True


class ProductionConfig(Config):
    """Production environment configuration"""
    ENV = "production"
    DEBUG_TB_INTERCEPT_REDIRECTS = False
