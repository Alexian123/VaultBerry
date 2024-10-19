from flask import jsonify, current_app
from app import db

# Example route
@current_app.route('/')
def home():
    return jsonify({"message": "Hello, World!"})