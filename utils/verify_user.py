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
