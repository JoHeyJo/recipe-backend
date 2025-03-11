from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
import traceback
from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from repository import highlight
from exceptions import *


    # if error_type == "TypeError":
    #     return jsonify({"error": error_message}), 400
    
    # elif error_type == "IntegrityError":
    #     return jsonify({"error": error_message}), 400
    
    # elif error_type == "ValueError" or "KeyError":
    #     return jsonify({"value error": error_message}), 400
    
    # elif error_type == "SQLAlchemyError":
    #     return jsonify({"error": "Database error", "details": error_message}), 500

    # return jsonify({"error": "Unexpected error", "type": error_type, "details": error_message}), 500


def route_error_handler(func):
    """Decorator to handle errors in Flask routes or services."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            highlight(e, "#")
            return handle_error(e)
    return wrapper


def handle_error(error):
    """Dynamically handles all errors based on type."""

    error_type = type(error).__name__  # Get original exception type
    error_message = str(error)
    tb = traceback.format_exc()

    print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK START ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
    print(tb)
    print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK END ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")

    error_code = None  # Default to None
    http_status = 500

    # Handle SQLAlchemy errors (Only access `orig` if it exists)
    if isinstance(error, IntegrityError):
        if hasattr(error, "orig") and hasattr(error.orig, "pgcode"):
            error_code = error.orig.pgcode  # PostgreSQL error code
        # elif hasattr(error, "orig") and hasattr(error.orig, "args"):
        #     error_code = error.orig.args[0]  # MySQL/SQLite error code

        # 23505 (Postgres) & 1062 (MySQL) = Duplicate Key Violation
        http_status = 400 if error_code in ["23505", "1062"] else 500

    elif isinstance(error, OperationalError):
        http_status = 500  # Database connection issues
    elif isinstance(error, SQLAlchemyError):
        http_status = 500  # Other SQLAlchemy errors

    # Handle Flask-specific HTTP errors
    elif isinstance(error, HTTPException):
        http_status = error.code

    # Handle built-in Python exceptions
    elif isinstance(error, ValueError):
        http_status = 400
    elif isinstance("error", KeyError):
        http_status = 400
    elif isinstance(error, TypeError):
        http_status = 400
    elif isinstance(error, UsernameAlreadyTakenError):
        http_status = 409

    # Return JSON response with dynamic status code

    
    highlight(error,"$")
    highlight((error_message,http_status),"$")
    return jsonify({
        "error": error_message,
        "type": error_type,
        "code": error_code,  # Include extracted error code (if available)
        "status": http_status
    }), http_status
