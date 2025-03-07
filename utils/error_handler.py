from flask import jsonify

def handle_error(error):
    if isinstance(error, ValueError):
        response = jsonify({"error": str(error)})
        response.status_code = 400
    elif isinstance(error, RuntimeError):
        response = jsonify({"error": str(error)})
        response.status_code = 500  # Internal Server Error
    else:
        response = jsonify({"error": "An unexpected error occurred."})
        response.status_code = 500
    return response
