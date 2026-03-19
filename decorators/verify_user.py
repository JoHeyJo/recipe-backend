from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.functions import highlight

def verify_jwt_identity(f):
    """Decorator that simply extracts and injects the verified user."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        kwargs['authed_user_id'] = current_user_id
        return f(*args, **kwargs)

    return decorated_function

