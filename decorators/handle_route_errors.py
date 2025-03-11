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
            error_code = getattr(e.orig, "pgcode", None)
            return handle_error(e, error_code)
    return wrapper


def handle_error(error, error_code):
    """Dynamically handles all errors based on type."""

    error_type = type(error).__name__  # Get original exception type
    error_message = str(error)
    tb = traceback.format_exc()

    print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK START ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
    print(tb) 
    print(error_code)
    print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK END ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")


    if error_type == "TypeError":
        return jsonify({"error": error_message}), 400
    
    elif error_type == "IntegrityError":
        return jsonify({"error": error_message}), 400
    
    elif error_type == "ValueError" or "KeyError":
        return jsonify({"value error": error_message}), 400
    
    elif error_type == "SQLAlchemyError":
        return jsonify({"error": "Database error", "details": error_message}), 500

    return jsonify({"error": "Unexpected error", "type": error_type, "details": error_message}), 500
