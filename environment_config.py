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
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    CLIENT_ORIGIN_URL = os.getenv("CLIENT_URL")
    AWS_REGION = os.getenv("AWS_REGION")
    SES_FROM_EMAIL = os.getenv("SES_FROM_EMAIL")
    FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL")
    SQLALCHEMY_ECHO = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = True


class ProductionConfig(Config):
    """Production environment configuration"""
    ENV = "production"
    DEBUG_TB_INTERCEPT_REDIRECTS = False
