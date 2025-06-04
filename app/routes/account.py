from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required
from app.models import User
from app.util import http
from app import db, scram, logger

account_bp = Blueprint("account", __name__)

@account_bp.route("", methods=["GET"])
@login_required
def get_account_info():
    user: User = current_user
    try:
        # The Account Info for the current user
        return jsonify(user.account_dict()), http.SuccessCode.OK.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("", methods=["PATCH"])
@login_required
def update_account_info():
    user: User = current_user
    try:
        data = request.get_json()
        account_data = data["account"]
        
        # Check if email is available
        existing_user: User = User.query.filter_by(email=account_data["email"]).first()
        if existing_user is not None and existing_user.id != user.id:
            raise http.RouteError("Email already in use", http.ErrorCode.CONFLICT)
        
        no_activation_required = data.get("no_activation_required", False)  # For testing purposes

        # Update the user
        new_email = account_data["email"]
        if new_email != user.email:
            if not no_activation_required:
                user.is_active = False
                user.verification_token = None
                user.token_expiration = None
            user.email = new_email
        user.first_name = account_data.get("first_name", user.first_name)
        user.last_name = account_data.get("last_name", user.last_name)
        db.session.commit()

        return jsonify({"message": "Account info updated successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("", methods=["DELETE"])
@login_required
def delete_account():
    user: User = current_user
    try:
        # Safety check: user must not be admin
        if user.is_admin():
            raise http.RouteError("Cannot delete admin user", http.ErrorCode.FORBIDDEN)

        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/password", methods=["PATCH"])
@login_required
def change_password():
    user: User = current_user
    try:
        data = request.get_json()
        passwords = data["passwords"]
        keychain = data["keychain"]
        reencrypt = data["re_encrypt"]
        
        if reencrypt:
            # Save the number of vault entries left to patch (initially the total)
            session[f"{user.id}_entries_left"] = len(user.entries)
            logger.info("Initialized re-encryption process")
        else:
            # Save 0 to signal no reencryption 
            session[f"{user.id}_entries_left"] = 0
        
        # Update the vault key secret
        user.set_vault_keychain(keychain["vault_key"], keychain["recovery_key"], keychain["salt"])
        
        # Update the SCRAM auth info
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(passwords["regular_password"])
        user.set_scram_auth_info(salt, stored_key, server_key, iteration_count)
        
        # Update reovery password
        user.set_recovery_password(passwords["recovery_password"])

        # Commit the changes if not reencrypting
        if not reencrypt:
            db.session.commit()
        else:
            db.session.flush()
            
        return jsonify({"message": "Password changed successfully"}), http.SuccessCode.OK.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/2fa/setup", methods=["POST"])
@login_required
def setup_2fa():
    user: User = current_user
    try:
        # Check if secret exists
        if user.mfa_enabled:
            raise http.RouteError("2FA already set up", http.ErrorCode.BAD_REQUEST)

        # Generate and save a new TOTP secret
        provisioning_uri, img_str = user.generate_totp_secret()
        db.session.commit()

        return jsonify({"provisioning_uri": provisioning_uri, "qrcode": img_str}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/2fa/status", methods=["GET"])
@login_required
def get_2fa_status():
    user: User = current_user
    try:
        # Return 2FA status
        return jsonify({"enabled": user.mfa_enabled}), http.SuccessCode.OK.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/2fa/disable", methods=["POST"])
@login_required
def disable_2fa():
    user: User = current_user
    try:
        # Check current status
        if not user.mfa_enabled:
            raise http.RouteError("2FA not set up", http.ErrorCode.BAD_REQUEST)

        # Set flag to false. The old secret does not need to be removed
        user.mfa_enabled = False
        db.session.commit()
        return jsonify({"message": "2FA disabled successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value