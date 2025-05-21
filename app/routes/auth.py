from flask import Blueprint, jsonify, request, session
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
import pickle
from scramp import ScramException
from app.models import User, Secret, OneTimePassword
from app.util import security, time, http
from app import logger, db, login_manager, mail, scram

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        account_info = data["account_info"]
        passwords = data["passwords"]
        keychain = data["keychain"]
        
        # Check if the user already exists
        existing_user = User.query.filter_by(email=account_info["email"]).first()
        if existing_user:
            raise http.RouteError("Email already in use", http.ErrorCode.CONFLICT)

        # Create the new user
        new_user = User(
            email=account_info["email"],
            first_name=account_info.get("first_name"),
            last_name=account_info.get("last_name"),
            created_at=time.get_now_timestamp()
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Create the default empty secrets for the new user
        Secret.create_default_secrets(new_user.id)
        
        # Store the revoery passcode
        new_user.set_recovery_password(passwords["recovery_password"])
        
        # Store the vault key and salt
        new_user.set_vault_keychain(keychain["vault_key"], keychain["recovery_key"], keychain["salt"])
        
        # Generate and store the SCRAM auth info as secrets
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(passwords["regular_password"])
        new_user.set_scram_auth_info(salt, stored_key, server_key, iteration_count)
        
        # Commit changes
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), http.SuccessCode.CREATED.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

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
            raise http.RouteError("User not found", http.ErrorCode.NOT_FOUND)
        
        # Check if the user is an admin
        if user.is_admin():
            raise http.RouteError("Cannot log in as admin", http.ErrorCode.FORBIDDEN)

        # Check if 2FA is enabled
        if user.mfa_enabled:
            if totp_code is None:  # The frontend should check for this exact error message
                raise http.RouteError("2FA required", http.ErrorCode.BAD_REQUEST)

            # Check the token
            if not user.verify_totp_code(totp_code):
                raise http.RouteError("Invalid TOTP token", http.ErrorCode.UNAUTHORIZED)
        
        # Create the SCRAM server
        scram_server = scram.make_server(User.get_auth_information)
        
        # Get server first message
        scram_server.set_client_first(client_first_message)
        server_first_message = scram_server.get_server_first()
        
        # Store the server in the session
        session[f"{user.id}_scram_server"] = pickle.dumps(scram_server)
         
        # Return the server's first message
        return jsonify({"server_message": server_first_message}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@auth_bp.route("/login/step2", methods=["POST"])
def login_step2():
    try:    
        data = request.get_json()
        email = data["email"]
        client_final_message = data["client_message"]
        
        # Find the user
        user: User = User.query.filter_by(email=email).first()
        if user is None:
            raise http.RouteError("User not found", http.ErrorCode.NOT_FOUND)
        
        # Do not allow admin login
        if user.is_admin():
            raise http.RouteError("Cannot log in as admin", http.ErrorCode.FORBIDDEN)
        
        # Grab the server from the session
        scram_server = pickle.loads(session[f"{user.id}_scram_server"])
        del session[f"{user.id}_scram_server"]
        
        # Get the server's final message
        scram_server.set_client_final(client_final_message)
        server_final_message = scram_server.get_server_final() 

        # Login the user
        login_user(user)
        
        # Return the server's evidence message 'M2' and the vault keychain
        return jsonify({"server_message": server_final_message, "keychain": user.get_vault_keychain_dict()}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except ScramException as e:
        return jsonify({"error": str(e)}), http.ErrorCode.UNAUTHORIZED.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Logout successful"}), http.SuccessCode.OK.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    
@auth_bp.route("/recovery/send", methods=["POST"])
def reovery_send():
    try:
        email = request.args.get("email")

        # Find user by email
        user: User = User.query.filter_by(email=email).first()
        if not user:
            raise http.RouteError("User not found", http.ErrorCode.NOT_FOUND)

        # Check if cooldown expired
        now = time.get_now_timestamp()
        last_otp: OneTimePassword = OneTimePassword.query.filter_by(user_id=user.id).order_by(OneTimePassword.created_at.desc()).first()
        if last_otp and last_otp.created_at > now - (60):  # change to 24 hours in seconds
            time_remaining = last_otp.created_at - (now - (60))
            error_message = f"Please try again in {time_remaining:.0f} seconds"
            raise http.RouteError(error_message, http.ErrorCode.BAD_REQUEST)

        # Generate a new OTP
        otp = security.generator.otp()
        expires_at = now + (5 * 60)  # 5 minutes in seconds
        one_time_password = OneTimePassword(
            user_id=user.id,
            otp=otp,
            created_at=now,
            expires_at=expires_at
        )
        db.session.add(one_time_password)

        # Send an email containing the OTP to the user
        msg = Message("Your Recovery OTP", recipients=[email])
        msg.body = f"Your OTP is: {otp}"
        msg.html = f"<p>Your OTP is: <strong>{otp}</strong></p>"
        mail.send(msg)

        db.session.commit()
        return jsonify({"message": "OTP sent successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@auth_bp.route("/recovery/login", methods=["POST"])
def recovery_login():
    try:
        data = request.get_json()
        email = data["email"]
        recovery_password = data["recovery_password"]
        otp = data["otp"]
        
        # Find the user by email
        user: User = User.query.filter_by(email=email).first()
        if not user:
            raise http.RouteError("User not found", http.ErrorCode.NOT_FOUND)

        # Check recovery password
        if not user.check_recovery_password(recovery_password):
            raise http.RouteError("Invalid recovery password", http.ErrorCode.UNAUTHORIZED)

        # Check OTP
        one_time_password: OneTimePassword = OneTimePassword.query.filter_by(otp=otp, user_id=user.id).first()
        now = time.get_now_timestamp()
        if one_time_password and not one_time_password.used and one_time_password.expires_at > now:
            # Mark OTP as used
            one_time_password.used = True

            if login_user(user):
                db.session.commit()
                
            return jsonify(user.get_vault_keychain_dict()), http.SuccessCode.OK.value

        raise http.RouteError("Invalid or expired OTP", http.ErrorCode.UNAUTHORIZED)
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value