from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from app.models import User, KeyChain, OneTimePassword
from app.util import generate_password_hash, check_password_hash, generate_otp, get_now_timestamp
from app import db, login_manager, mail

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@auth_bp.route('/recovery', methods=['GET'])
def get_recovery_otp():
    try:
        email = request.args.get('email')

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "No user with this email exists"}), 401

        # Check if cooldown expired
        now = get_now_timestamp()
        last_otp = OneTimePassword.query.filter_by(user_id=user.id).order_by(OneTimePassword.created_at.desc()).first()
        if last_otp and last_otp.created_at > now - (60):  # change to 24 hours in seconds
            time_remaining = last_otp.created_at - (now - (60))
            error_message = f'Please try again in {time_remaining:.0f} seconds'
            return jsonify({"error": error_message}), 400

        # Generate OTP
        otp = generate_otp()
        expires_at = now + (5 * 60)  # 5 minutes in seconds
        one_time_password = OneTimePassword(
            user_id=user.id, 
            otp=otp, 
            created_at=now,
            expires_at=expires_at
        )
        db.session.add(one_time_password)
        db.session.commit()
        
        msg = Message('Your Recovery OTP', recipients=[email])
        msg.body = f'Your OTP is: {otp}'
        msg.html = f"<p>Your OTP is: <strong>{otp}</strong></p>"
        mail.send(msg)

        return jsonify({'message': 'OTP sent successfully'}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/recovery", methods=['POST'])
def recovery_login():
    try:
        data = request.json
        email = data['email']
        otp = data['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "No user with this email exists"}), 401

        # Check OTP
        one_time_password = OneTimePassword.query.filter_by(otp=otp, user_id=user.id).first()
        now = get_now_timestamp()
        if one_time_password and not one_time_password.used and one_time_password.expires_at > now:
            keychain = KeyChain.query.filter_by(id=user.keychain_id).first()
            if not keychain:
                return jsonify({"error": "Inexistent keychain"}), 400
            
            one_time_password.used = True
            db.session.commit()
            login_user(user)
            
            return jsonify(keychain.to_dict()), 200

        return jsonify({'error': 'Invalid or expired OTP.'}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        account_data = request.json['account']
        keychain_data = request.json['keychain']
        password = request.json['password']

        existing_user = User.query.filter_by(email=account_data['email']).first()
        if existing_user:
            return jsonify({"error": "Email already in use"}), 400

        # Create a keychain for the new user
        keychain = KeyChain(
            salt=keychain_data['salt'],
            vault_key=keychain_data['vault_key'] ,
            recovery_key=keychain_data['recovery_key'],
        )
        db.session.add(keychain)
        db.session.commit()

        new_user = User(
            keychain_id=keychain.id,
            email=account_data['email'],
            hashed_password=generate_password_hash(password),
            first_name=account_data.get('first_name'),
            last_name=account_data.get('last_name'),
            created_at=get_now_timestamp()
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data['email']
        password = data['password']

        # Find the user
        user = User.query.filter_by(email=email).first()
        
        # Check if password is correct
        if user and check_password_hash(user.hashed_password, password):
             # Find the keychain
            keychain = KeyChain.query.filter_by(id=user.keychain_id).first()
            if not keychain:
                return jsonify({"error": "Inexistent keychain"}), 400
            
            login_user(user)
            return jsonify(keychain.to_dict()), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400