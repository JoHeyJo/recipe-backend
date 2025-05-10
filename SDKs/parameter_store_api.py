import boto3

# Create a Systems Manager client
ssm = boto3.client('ssm', region_name='us-west-1')

def fetch_secrets(app):
	"""Centralizes access point to parameter store"""

	# access and FLASK_SECRET_KEY
	parameter = ssm.get_parameter(Name='FLASK_SECRET_KEY', WithDecryption=True)
	secret_key_flask = parameter['Parameter']['Value']
	app.secret_key_flask = secret_key_flask

 # access and JWT_SECRET_KEY
	parameter = ssm.get_parameter(Name='JWT_SECRET_KEY', WithDecryption=True)
	secret_key_jwt = parameter['Parameter']['Value']
	app.secret_key_jwt = secret_key_jwt

 # access and DATABASE_URI
	parameter = ssm.get_parameter(Name='DATABASE_URI', WithDecryption=True)
	DATABASE_URI = parameter['Parameter']['Value']
	app.DATABASE_URI = DATABASE_URI


