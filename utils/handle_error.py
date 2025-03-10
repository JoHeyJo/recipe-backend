from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def handle_error(error):
    """Dynamically handles all errors based on type."""

    error_type = type(error).__name__  # Get original exception type
    error_message = str(error)

    print("!!!!!!!!!!!!!!!!")

    
    if isinstance(error, TypeError):
        return jsonify({"error": error_message})
    elif isinstance(error,KeyError):
        print("%%%%%%%%%%%%%")
    elif isinstance(error, IntegrityError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, ValueError):
        return jsonify({"error": error_message}), 400
    elif isinstance(error, SQLAlchemyError):
        return jsonify({"error": "Database error", "details": error_message}), 500

    return jsonify({"error": "Unexpected error", "type": error_type, "details": error_message}), 500
