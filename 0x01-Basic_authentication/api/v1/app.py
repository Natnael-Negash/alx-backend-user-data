#!/usr/bin/env python3
"""
Route module for the API
"""

from os import getenv
from api.v1.views import app_views
from api.v1.auth.auth import Auth
from api.v1.auth.basic_auth import BasicAuth
from flask import Flask, jsonify, abort, request
from flask_cors import CORS

app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = None

# Set up authentication based on environment variable
if getenv("AUTH_TYPE") == "auth":
    auth = Auth()
elif getenv("AUTH_TYPE") == "basic_auth":
    auth = BasicAuth()


@app.errorhandler(404)
def not_found(error) -> str:
    """Handler for 404 Not Found errors"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """Handler for 401 Unauthorized errors"""
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """Handler for 403 Forbidden errors"""
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def before_request():
    """
    Handler for actions to take before each request.
    Checks for authentication and authorization.
    """
    authorized_list = ['/api/v1/status',
                       '/api/v1/unauthorized/', '/api/v1/forbidden']

    # If auth is set and the request requires authorization
    if auth and auth.require_auth(request.path, authorized_list):
        # Check for authorization header
        if not auth.authorization_header(request):
            abort(401)
        # Check for current user
        if not auth.current_user(request):
            abort(403)


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port)
