import boto3
from utils.functions import highlight

# Create a Systems Manager client
ssm = boto3.client('ssm', region_name='us-west-1')

# needs error handling
def fetch_secrets(app):
    """Centralizes access point to parameter store"""

    # access and FLASK_SECRET_KEY
    parameter = ssm.get_parameter(Name='SECRET_KEY', WithDecryption=True)
    secret_key_flask = parameter['Parameter']['Value']
    app.config["SECRET_KEY"] = secret_key_flask

   # access and JWT_SECRET_KEY
    parameter = ssm.get_parameter(Name='JWT_SECRET_KEY', WithDecryption=True)
    secret_key_jwt = parameter['Parameter']['Value']
    app.config["JWT_SECRET_KEY"] = secret_key_jwt

   # access and DATABASE_URI
    parameter = ssm.get_parameter(Name='DATABASE_URI', WithDecryption=True)
    database_uri = parameter['Parameter']['Value']
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
