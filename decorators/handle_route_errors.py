from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, OperationalError
import traceback
from functools import wraps
from flask import jsonify, current_app
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
    """Dynamically creates error payload based on status/exception."""
    error_type_name = type(error).__name__
    error_code = None
    http_status = 500

    # Default message
    error_message = str(error)

    # SQLAlchemy errors
    if isinstance(error, IntegrityError):
        if hasattr(error, "orig") and hasattr(error.orig, "pgcode"):
            error_code = error.orig.pgcode
        http_status = 400 if error_code in ["23505", "1062"] else 500

    elif isinstance(error, (OperationalError, SQLAlchemyError)):
        http_status = 500

    # Flask/Werkzeug HTTP errors (404, 401, etc.)
    elif isinstance(error, HTTPException):
        http_status = error.code
        # Better message for HTTP exceptions
        error_message = getattr(error, "description", error_message)

    # App-level expected errors
    elif isinstance(error, ForbiddenError):
        http_status = 403

    elif isinstance(error, KeyError):
        http_status = 400
        error_message = f"Missing required field: {error.args[0]}"

    elif isinstance(error, (EmailAlreadyRegisteredError, UsernameAlreadyTakenError, SignUpError)):
        http_status = 409
    highlight(current_app,"$")
    # Logging (optional: only traceback for 5xx)
    tb = traceback.format_exc()
    if http_status >= 500:
        error_message = "Internal server error."
        print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK START ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
        print(tb)
        print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️ ERROR TRACEBACK END ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
        if current_app.debug:
            raise error
    else:
        print(f"⚠️⚠️⚠️⚠️⚠️⚠️⚠️ {error_type_name}: {error_message}")

    return jsonify({
        "error": error_message,
        "type": error_type_name,
        "code": error_code,
        "status": http_status
    }), http_status

