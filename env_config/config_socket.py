from flask_socketio import SocketIO

def configure_socket(app):
    """Dynamically configure SocketIO based on environment"""
    if app.config['ENV'] == 'production':
        return SocketIO(app, cors_allowed_origins=app.config["CLIENT_ORIGIN_URL"])
    else:
        # return SocketIO(app, cors_allowed=app.config["CLIENT_URL"])
        return SocketIO(app, cors_allowed_origins="*")
