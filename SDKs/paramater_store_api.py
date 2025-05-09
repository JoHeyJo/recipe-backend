import boto3

# Create a Systems Manager client
ssm = boto3.client('ssm', region_name='us-west-1')

def fetch_flask_secret(app):
	parameter = ssm.get_parameter(Name='FLASK_SECRET_KEY', WithDecryption=True)
	secret_key_flask = parameter['Parameter']['Value']
	app.secret_key_flask = secret_key_flask

def fetch_jwt_secret(app):
	parameter = ssm.get_parameter(Name='JWT_SECRET_KEY', WithDecryption=True)
	secret_key_jwt = parameter['Parameter']['Value']
	app.secret_key_jwt = secret_key_jwt


