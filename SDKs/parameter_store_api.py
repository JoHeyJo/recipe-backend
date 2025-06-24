import boto3
from utils.functions import highlight
import logging
from botocore.exceptions import BotoCoreError, ClientError
logger = logging.getLogger(__name__)

# Create a Systems Manager client
ssm = boto3.client('ssm', region_name='us-west-1')

# needs error handling

def fetch_secrets(app):
    """Centralizes access point to parameter store"""
    try:
        # access FLASK_SECRET_KEY
        parameter = ssm.get_parameter(Name='SECRET_KEY', WithDecryption=True)
        secret_key_flask = parameter['Parameter']['Value']
        app.config["SECRET_KEY"] = secret_key_flask

        # access JWT_SECRET_KEY
        parameter = ssm.get_parameter(
            Name='JWT_SECRET_KEY', WithDecryption=True)
        secret_key_jwt = parameter['Parameter']['Value']
        app.config["JWT_SECRET_KEY"] = secret_key_jwt

        # access DATABASE_URI
        parameter = ssm.get_parameter(Name='DATABASE_URI', WithDecryption=True)
        database_uri = parameter['Parameter']['Value']
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

        # access Client Origin
        parameter = ssm.get_parameter(Name='/CodeBuild/client_origin', WithDecryption=True)
        client_url = parameter['Parameter']['Value']
        app.config["CLIENT_ORIGIN_URL"] = client_url
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Error fetching secrets from Parameter Store: {e}")
        raise RuntimeError(f"Secrets retrieval failed") from e
