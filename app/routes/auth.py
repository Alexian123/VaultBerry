from flask import Blueprint, jsonify, request, session, current_app, url_for
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
        no_activation_required = data.get("no_activation_required", False)  # For testing purposes
        
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
        if no_activation_required:
            new_user.is_activated = True

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
    
@auth_bp.route("/activation/send", methods=["POST"])
def activation_send():
    try:
        email = request.args.get("email")
        
        # Find user by email
        user: User = User.query.filter_by(email=email).first()
        if not user:
            raise http.RouteError("User not found", http.ErrorCode.NOT_FOUND)
        
        # Check if cooldown expired
        time_remaining = OneTimePassword.get_cooldown_remaining_seconds_for_user(user.id, "ACTIVATION", 30*60)
        if time_remaining > 0:
            error_message = f"Am activation email has already been sent.\n"
            error_message += f"Please try again in {int(time_remaining/60//60)} hours, "
            error_message += f"{int((time_remaining/60)%60)} minutes, and {int(time_remaining%60)} seconds."
            raise http.RouteError(error_message, http.ErrorCode.BAD_REQUEST)
        
        # New: Generate verification token and send email
        token = OneTimePassword.create_email_verification_otp(user.id)
        
        # Construct the verification URL using the base URL from config
        verification_link = f"{current_app.config['BASE_URL']}{url_for('auth.activate', id=user.id, token=token, _external=False)}"

        # Send the link via email
        msg = Message("Verify Your Email Address", recipients=[user.email])
        msg.body = f"Please click the following link to verify your email: {verification_link}"
        msg.html = f"<p>Please click the following link to verify your email: <a href='{verification_link}'>{verification_link}</a></p>"
        mail.send(msg)
        
        db.session.commit()
        return jsonify({"message": "Verification email sent successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during email verification: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while sending the email"}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    
@auth_bp.route("/activation/<int:id>/<token>", methods=["GET"])
def activate(id: int, token: str):
    try:
        # Find the user
        user: User = User.query.filter_by(id=id).first()
        if not user:
            raise http.RouteError("User not found", http.ErrorCode.BAD_REQUEST)
        
        # Check if the token is valid and not expired
        if user.verify_and_use_otp(token):
            user.is_activated = True
            db.session.commit()
            return jsonify({"message": "Email verified successfully"}), http.SuccessCode.OK.value
        else:
            raise http.RouteError("Invalid or expired verification token.", http.ErrorCode.BAD_REQUEST)

    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during email verification: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred during email verification"}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

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
            raise http.RouteError("Cannot log in as admin", http.ErrorCode.UNAUTHORIZED)
        
        # Check if the user is activated
        if not user.is_activated:
            raise http.RouteError("User not activated", http.ErrorCode.FORBIDDEN)

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
        time_remaining = OneTimePassword.get_cooldown_remaining_seconds_for_user(user.id, "RECOVERY", 24*60*60)
        if time_remaining > 0:
            error_message = f"A recovery email has already been sent.\n"
            error_message += f"Please try again in {int(time_remaining/60//60)} hours, "
            error_message += f"{int((time_remaining/60)%60)} minutes, and {int(time_remaining%60)} seconds."
            raise http.RouteError(error_message, http.ErrorCode.BAD_REQUEST)

        # Generate a new OTP
        otp = OneTimePassword.create_recovery_otp(user.id, 5*60)

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
        
        # Check if the user is activated
        if not user.is_activated:
            raise http.RouteError("User not activated", http.ErrorCode.FORBIDDEN)

        # Check recovery password
        if not user.check_recovery_password(recovery_password):
            raise http.RouteError("Invalid recovery password", http.ErrorCode.UNAUTHORIZED)

        # Check OTP
        if user.verify_and_use_otp(otp):
            if login_user(user):
                db.session.commit()
            return jsonify(user.get_vault_keychain_dict()), http.SuccessCode.OK.value

        raise http.RouteError("Invalid or expired OTP", http.ErrorCode.UNAUTHORIZED)
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value