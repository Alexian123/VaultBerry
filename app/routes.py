from flask import Blueprint, jsonify, request
from app.models import User, VaultEntry 
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return jsonify({"message": "Hello, Flask!"})

@auth_bp.route('/users')
def get_posts():
    users = User.query.all()
    return {'users': [user.email for user in users]}

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data['email']
    password = data['password']
    
    # Hash the password on the backend
    hashed_password = generate_password_hash(password)
    
    # Save the user with hashed password
    new_user = User(email=email, hashed_password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    
    # Find the user
    user = User.query.filter_by(email=email).first()
    
    # Check if password is correct
    if user and check_password_hash(user.hashed_password, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401