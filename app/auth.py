from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db, login_manager

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@auth_bp.route('/')
def home():
    return jsonify({"message": "Hello, Flask!"})

@auth_bp.route('/users')
def get_users():
    try:
        users = User.query.all()
        return jsonify({"users": [user.to_dict() for user in users]}), 200
    except Exception as e:
        return jsonify({"message": "User registration failed", "error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    try:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "Email already in use"}), 400

        new_user = User(
            email=data['email'],
            salt=data['salt'],
            hashed_password=generate_password_hash(data['password']),
            vault_key=data['vault_key'] ,
            recovery_key=data['recovery_key'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "User registration failed", "error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    
    try:
        # Find the user
        user = User.query.filter_by(email=email).first()
        
        # Check if password is correct
        if user and check_password_hash(user.hashed_password, password):
            login_user(user)
            return jsonify({"user": user.to_dict()})
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 400

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        return jsonify({"message": "Logout failed", "error": str(e)}), 400