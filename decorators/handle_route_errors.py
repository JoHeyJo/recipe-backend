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

import traceback
from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from repository import highlight


def route_error_handler(func):
    """Decorator to handle errors in Flask routes or services."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return handle_error(e) 
    return wrapper


def handle_error(error):
    """Dynamically handles all errors based on type."""

    error_type = type(error).__name__  # Get original exception type
    error_message = str(error)

    highlight(error,"#")
    highlight(error_type,"#")
    highlight(error_message,"#")
    highlight(type(error),"#")

    # Capture the full traceback and log it
    tb = traceback.format_exc()
    print("⚠️ ERROR TRACEBACK START ⚠️")
    print(tb)  # ✅ Logs full traceback
    print("⚠️ ERROR TRACEBACK END ⚠️")

    if error_type == "KeyError":
        return jsonify({"error": error_message})

    if isinstance(error, TypeError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, IntegrityError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, ValueError or KeyError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, SQLAlchemyError):
        return jsonify({"error": "Database error", "details": error_message}), 500

    return jsonify({"error": "Unexpected error", "type": error_type, "details": error_message}), 500
