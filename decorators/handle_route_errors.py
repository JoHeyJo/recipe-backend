from functools import wraps
from flask import jsonify
from utils import error_handler


def error_handler(func):
    """Decorator to handle errors in Flask routes or services."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return error_handler(e)
    return wrapper
