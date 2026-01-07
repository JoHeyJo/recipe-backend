from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
import traceback
from functools import wraps
from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from exceptions import *
from utils.functions import highlight

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

    error_type_name = type(error).__name__  # Get original exception type
    error_message = str(error)
    tb = traceback.format_exc()
    error_type = type(error)

    print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK START ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
    print(tb)
    print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK END ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")

    error_code = None  # Default to None
    http_status = 500
    # Handle SQLAlchemy errors (Only access `orig` if it exists)
    if issubclass(error_type, IntegrityError):
        if hasattr(error, "orig") and hasattr(error.orig, "pgcode"):
            error_code = error.orig.pgcode  # PostgreSQL error code
        # 23505 (Postgres) & 1062 (MySQL) = Duplicate Key Violation
        http_status = 400 if error_code in ["23505", "1062"] else 500

    elif issubclass(error_type, OperationalError):
        http_status = 500  # Database connection issues
    elif issubclass(error_type, SQLAlchemyError):
        http_status = 500  # Other SQLAlchemy errors

    # Handle Flask-specific HTTP errors
    elif issubclass(error_type, HTTPException):
        http_status = error.code

    # Handle built-in Python exceptions
    elif issubclass(error_type, (ValueError, AttributeError)):
        http_status = 400
    elif issubclass(error_type, KeyError):
        http_status = 400
    elif issubclass(error_type, TypeError):
        http_status = 400
    elif issubclass(error_type, NotFound):
        http_status = 404
    elif issubclass(error_type, (EmailAlreadyRegisteredError, UsernameAlreadyTakenError, SignUpError)):
        http_status = 409

    highlight([error_message, error_code, http_status])
    return jsonify({
        "error": error_message,
        "type": error_type_name,
        "code": error_code,  # Include extracted error code (if available)
        "status": http_status
    }), http_status
