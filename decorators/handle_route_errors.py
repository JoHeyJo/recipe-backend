# from functools import wraps
# from flask import jsonify
# from utils import handle_error


# def route_error_handler(func):
#     """Decorator to handle errors in Flask routes or services."""
#     print("$$$$$$$$$")
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             return handle_error(e)
#     return wrapper


from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


def route_error_handler(func):
    """Decorator to handle errors in Flask routes or services."""
    print("%%%%%%%%%%%%%%%%%")  # Debugging output
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return handle_error(e)  # ✅ Call handle_error, not error_handler!
    return wrapper


def handle_error(error):
    """Dynamically handles all errors based on type."""

    error_type = type(error).__name__  # Get original exception type
    error_message = str(error)

    print("!!!!!!!!!!!!!!!!")  # Debugging output

    if isinstance(error, TypeError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, IntegrityError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, ValueError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, SQLAlchemyError):
        return jsonify({"error": "Database error", "details": error_message}), 500

    return jsonify({"error": "Unexpected error", "type": error_type, "details": error_message}), 500
