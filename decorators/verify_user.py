from functools import wraps
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity

def check_user_identity(f):
    """Decorator to handle user verification in routes."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        if str(current_user_id) != str(kwargs.get('user_id')):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)
        return f(*args, **kwargs)

    return decorated_function

