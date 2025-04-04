from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
import pickle
from app.models import User, Secret, OneTimePassword
from app.util import security, time
from app import logger, db, login_manager, mail, scram

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# @auth_bp.route("/recovery", methods=["POST"])
# def get_recovery_otp():
#     try:
#         email = request.args.get("email")

#         # Find user by email
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify({"error": "No user with this email exists"}), 401

#         # Check if cooldown expired
#         now = time.get_now_timestamp()
#         last_otp = OneTimePassword.query.filter_by(user_id=user.id).order_by(OneTimePassword.created_at.desc()).first()
#         if last_otp and last_otp.created_at > now - (60):  # change to 24 hours in seconds
#             time_remaining = last_otp.created_at - (now - (60))
#             error_message = f"Please try again in {time_remaining:.0f} seconds"
#             return jsonify({"error": error_message}), 400

#         # Generate a new OTP
#         otp = security.generator.otp()
#         expires_at = now + (5 * 60)  # 5 minutes in seconds
#         one_time_password = OneTimePassword(
#             user_id=user.id,
#             otp=otp,
#             created_at=now,
#             expires_at=expires_at
#         )
#         db.session.add(one_time_password)
#         db.session.commit()

#         # Send an email containing the OTP to the user
#         msg = Message("Your Recovery OTP", recipients=[email])
#         msg.body = f"Your OTP is: {otp}"
#         msg.html = f"<p>Your OTP is: <strong>{otp}</strong></p>"
#         mail.send(msg)

#         return jsonify({"message": "OTP sent successfully"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# @auth_bp.route("/recovery", methods=["POST"])
# def recovery_login():
#     try:
#         data = request.json
#         email = data["email"]
#         recovery_password = data["password"]
#         otp = data["token"]

#         # Find the user by email
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify({"error": "No user with this email exists"}), 401

#         # Check recovery password
#         if not security.hasher.check(user.hashed_recovery_password, recovery_password):
#             return jsonify({"error": "Invalid credentials"}), 401

#         # Check OTP
#         one_time_password = OneTimePassword.query.filter_by(otp=otp, user_id=user.id).first()
#         now = time.get_now_timestamp()
#         if one_time_password and not one_time_password.used and one_time_password.expires_at > now:

#             # Check keychain
#             keychain = KeyChain.query.filter_by(id=user.keychain_id).first()
#             if not keychain:
#                 return jsonify({"error": "Inexistent keychain"}), 400

#             # Mark OTP as used
#             one_time_password.used = True
#             db.session.commit()

#             login_user(user)
#             return jsonify(keychain.to_dict()), 200

#         return jsonify({"error": "Invalid or expired OTP."}), 401
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        # Check if the user already exists
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user:
            return jsonify({"error": "Email already in use"}), 400

        # Create the new user
        new_user = User(
            email=data["email"],
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            created_at=time.get_now_timestamp()
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Create the default empty secrets for the new user
        Secret.create_default_secrets(new_user.id)
        
        # Store the vault key and salt
        new_user.set_vault_key_secret(data["vault_key"], data["salt"])
        
        # Generate and store the SCRAM auth info as secrets
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(data["password"])
        new_user.set_scram_auth_info(salt, stored_key, server_key, iteration_count)
        
        # Commit changes
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/login/step1", methods=["POST"])
def login_step1():
    try:
        data = request.get_json()
        email = data["email"]
        client_first_message = data["client_message"]
        totp_code = data.get("code")
        
        # Find the user
        user: User = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        # Check if the user is an admin
        if user.is_admin:
            return jsonify({"error", "Cannot log in as admin"}), 401

        # Check if 2FA is enabled
        if user.mfa_enabled:
            if totp_code is None:  # The frontend should check for this exact error message
                return jsonify({"error": "2FA required"}), 401

            # Check the token
            if not user.verify_totp_code(totp_code):
                return jsonify({"error": "Invalid TOTP token"}), 401
        
        # Create the SCRAM server
        scram_server = scram.make_server(User.get_auth_information)
        
        # Get server first message
        scram_server.set_client_first(client_first_message)
        server_first_message = scram_server.get_server_first()
        
        # Store the server in the session
        session[f"{email}_scram_server"] = pickle.dumps(scram_server)
         
        # Return the server's first message
        return jsonify({"server_message": server_first_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/login/step2", methods=["POST"])
def login_step2():
    try:    
        data = request.get_json()
        email = data["email"]
        client_final_message = data["client_message"]
        
        # Find the user
        user: User = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"error": "User not found"}), 401
        
        # Do not allow admin login
        if user.is_admin():
            return jsonify({"error": "Cannot log in as admin"}), 401
        
        # Get encoded vault key and salt
        encoded_key, encoded_salt = user.get_vault_key_secret()
        
        # Grab the server from the session
        scram_server = pickle.loads(session[f"{email}_scram_server"])
        del session[f"{email}_scram_server"]
        
        # Get the server's final message
        scram_server.set_client_final(client_final_message)
        server_final_message = scram_server.get_server_final() 

        # Login the user
        login_user(user)
        
        # Return the server's evidence message 'M2' and the vault keychain
        return jsonify({"server_message": server_final_message, "vault_key": encoded_key, "salt": encoded_salt}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400