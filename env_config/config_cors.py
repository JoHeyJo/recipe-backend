from flask_cors import CORS

def configure_cors(app):
    """Dynamically handle configuration of CORS based on environment"""
    if app.config['ENV'] == 'production':
        CORS(app,
             origins=app.config["CLIENT_ORIGIN_URL"],
             supports_credentials=True,
             methods=["GET", "POST", "OPTIONS", "PATCH", "DELETE"],
             allow_headers=["Content-Type", "Authorization"])
    else:
        # CORS(app, resources={r"/*": {"origins": {os.environ["CLIENT_URL"]}}})
        CORS(app)   