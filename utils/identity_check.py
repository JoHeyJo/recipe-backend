# Centralize the Identity Check
# Create a decorator or utility function for this check to ensure consistency 
# across all routes and reduce repetitive code.


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

# implement
# @app.get("/users/<user_id>")
# @jwt_required()
# @verify_user_access
# def get_user(user_id):

# Use Python’s Logging Module to record unauthorized attempts
# The logging module allows you to log messages to a file, console, or external 
# logging service. For auditing, it’s ideal to log unauthorized access attempts
#  to a file or a dedicated logging system like ELK(Elasticsearch, Logstash, Kibana).


# import logging

# # Configure the logger
# logging.basicConfig(
#     filename="access_audit.log",  # Log file
#     level=logging.WARNING,       # Log level
#     format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
# )

# from flask import request
# from flask_jwt_extended import get_jwt_identity


# def log_unauthorized_access(identity, user_id):
#     logging.warning(
#         "Unauthorized access attempt detected. "
#         f"JWT Identity: {identity}, Requested User ID: {user_id}, "
#         f"IP: {request.remote_addr}, Endpoint: {request.path}"
#     )

# Integrate into routes
# Check if the identity matches the user_id
# if str(identity) != str(user_id):  # Ensure type consistency
#     log_unauthorized_access(identity, user_id)  # Log the attempt
#     return jsonify({"msg": "Unauthorized access"}), 403


# Advanced Logging Features
# You can include more details in your logs for better auditing:

# User-Agent: Helps identify the client making the request.
# Headers: Provide context for debugging(exclude sensitive headers like Authorization).
# Request Body: Useful if the request contains relevant data


# def log_unauthorized_access(identity, user_id):
#     logging.warning(
#         "Unauthorized access attempt detected. "
#         f"JWT Identity: {identity}, Requested User ID: {user_id}, "
#         f"IP: {request.remote_addr}, Endpoint: {request.path}, "
#         f"User-Agent: {request.headers.get('User-Agent')}, "
#         f"Headers: {dict(request.headers)}"
#     )

# For easier parsing and searching(e.g., in ELK or other logging tools), 
# use JSON formatting:

# import json


# def log_unauthorized_access(identity, user_id):
#     log_data = {
#         "event": "unauthorized_access",
#         "identity": identity,
#         "requested_user_id": user_id,
#         "ip": request.remote_addr,
#         "endpoint": request.path,
#         "user_agent": request.headers.get("User-Agent"),
#         "headers": dict(request.headers),
#     }
#     logging.warning(json.dumps(log_data))

# For scalable and searchable logging, consider sending audit logs to external systems like:

# Cloud Logging Services: AWS CloudWatch, Google Cloud Logging, Azure Monitor.
# Log Aggregators: ELK stack, Datadog, Splunk, or Sentry.

# import logging
# import watchtower

# # Add CloudWatch handler
# cloudwatch_handler = watchtower.CloudWatchLogHandler(
#     log_group="flask-access-audit")
# logging.getLogger().addHandler(cloudwatch_handler)

# # Log unauthorized access
# log_unauthorized_access("user123", "1")
