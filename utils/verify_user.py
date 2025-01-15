# from functools import wraps
# from flask import request, jsonify
# from flask_jwt_extended import get_jwt_identity


# def verify_user_access(route_function):
#     @wraps(route_function)
#     def wrapper(user_id, *args, **kwargs):
#         identity = get_jwt_identity()
#         if str(identity) != str(user_id):  # Ensure type consistency
#             return jsonify({"msg": "Unauthorized access"}), 403
#         return route_function(user_id, *args, **kwargs)
#     return wrapper
from functools import wraps
from flask import request, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from repository import highlight


def check_user_identity(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        highlight((current_user_id, kwargs.get('user_id')), "@")
        if str(current_user_id) != str(kwargs.get('user_id')):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)
        return f(*args, **kwargs)

    return decorated_function

