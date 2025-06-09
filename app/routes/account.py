from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required
from app.models import User
from app.util import http, security
from app import db, scram, logger

account_bp = Blueprint("account", __name__)

@account_bp.route("", methods=["GET"])
@login_required
def get_account_info():
    user: User = current_user
    logger.info(f"Attempting to retrieve account information for user ID: {user.id}")
    try:
        # The Account Info for the current user
        account_data = user.account_dict()
        logger.info(f"Account information successfully retrieved for user ID: {user.id}")
        return jsonify(account_data), http.SuccessCode.OK.value
    except Exception as e:
        logger.error(f"Error retrieving account information for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("", methods=["PATCH"])
@login_required
def update_account_info():
    user: User = current_user
    logger.info(f"Attempting to update account information for user ID: {user.id}")
    try:
        data = request.get_json()
        account_data = data["account"]
        
        # Check if email is available
        existing_user: User = User.query.filter_by(email=account_data["email"]).first()
        if existing_user is not None and existing_user.id != user.id:
            logger.warning(f"Account update failed for user ID: {user.id}. Email '{account_data['email']}' is already in use by another user.")
            raise http.RouteError("Email already in use", http.ErrorCode.CONFLICT)
        
        no_activation_required = data.get("no_activation_required", False) 

        # Update the user
        new_email = account_data["email"]
        if new_email != user.email:
            logger.info(f"User ID: {user.id} changing email from '{user.email}' to '{new_email}'.")
            if not no_activation_required:
                user.is_activated = False
                logger.info(f"User ID: {user.id} activation status set to False due to email change.")
            user.email = new_email
        user.first_name = account_data.get("first_name", user.first_name)
        user.last_name = account_data.get("last_name", user.last_name)
        db.session.commit()
        logger.info(f"Account information successfully updated for user ID: {user.id}.")
        return jsonify({"message": "Account info updated successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"Account update failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during account information update for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/delete", methods=["POST"])
@login_required
def delete_account():
    user: User = current_user
    logger.info(f"Attempting to delete account for user ID: {user.id}")
    try:
        # Safety check: user must not be admin
        if user.is_admin():
            logger.warning(f"Account deletion failed for user ID: {user.id}. Cannot delete admin user.")
            raise http.RouteError("Cannot delete admin user", http.ErrorCode.FORBIDDEN)
        
        # Check password hash
        data = request.get_json()
        password = data["password"] # Do not log the password
        if not security.hasher.check(user.hashed_password, password):
            logger.warning(f"Account deletion failed for user ID: {user.id}. Incorrect password provided.")
            raise http.RouteError("Incorrect password", http.ErrorCode.UNAUTHORIZED)

        # Delete the user
        user_id = user.id # Capture user ID before deletion
        db.session.delete(current_user)
        db.session.commit()
        logger.info(f"Account successfully deleted for user ID: {user_id}.")
        return jsonify({"message": "Account deleted successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"Account deletion failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during account deletion for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/password", methods=["PATCH"])
@login_required
def change_password():
    user: User = current_user
    logger.info(f"Attempting to change password for user ID: {user.id}")
    try:
        data = request.get_json()
        passwords = data["passwords"] # Do not log password details
        keychain = data["keychain"] # Do not log keychain details
        reencrypt = data["re_encrypt"]
        
        if reencrypt:
            # Save the number of vault entries left to patch (initially the total)
            session[f"{user.id}_entries_left"] = len(user.entries)
            logger.info(f"Initialized re-encryption process for user ID: {user.id}. Number of entries: {len(user.entries)}")
        else:
            # Save 0 to signal no reencryption 
            session[f"{user.id}_entries_left"] = 0
            logger.info(f"No re-encryption initiated for user ID: {user.id}.")
        
        # Update the vault key secret
        user.set_vault_keychain(keychain["vault_key"], keychain["recovery_key"], keychain["salt"])
        logger.debug(f"Vault keychain updated for user ID: {user.id}.")
        
        # Update the SCRAM auth info
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(passwords["regular_password"])
        user.set_scram_auth_info(salt, stored_key, server_key, iteration_count)
        logger.debug(f"SCRAM authentication information updated for user ID: {user.id}.")
        
        # Update reovery password
        user.set_recovery_password(passwords["recovery_password"])
        logger.debug(f"Recovery password updated for user ID: {user.id}.")

        # Commit the changes if not reencrypting
        if not reencrypt:
            db.session.commit()
            logger.info(f"Password changed successfully for user ID: {user.id} (no re-encryption needed).")
        else:
            db.session.flush()
            logger.info(f"Password changed successfully for user ID: {user.id}. Database flushed for re-encryption.")
            
        return jsonify({"message": "Password changed successfully"}), http.SuccessCode.OK.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during password change for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/2fa/setup", methods=["POST"])
@login_required
def setup_2fa():
    user: User = current_user
    logger.info(f"Attempting to set up 2FA for user ID: {user.id}")
    try:
        # Check if secret exists
        if user.mfa_enabled:
            logger.warning(f"2FA setup failed for user ID: {user.id}. 2FA is already set up.")
            raise http.RouteError("2FA already set up", http.ErrorCode.BAD_REQUEST)

        # Generate and save a new TOTP secret
        provisioning_uri, img_str = user.generate_totp_secret()
        db.session.commit()
        logger.info(f"2FA setup successful for user ID: {user.id}. Provisioning URI generated.")
        return jsonify({"provisioning_uri": provisioning_uri, "qrcode": img_str}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"2FA setup failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during 2FA setup for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    
    
@account_bp.route("/2fa/activate", methods=["POST"])
@login_required
def activate_2fa():
    user: User = current_user
    logger.info(f"Attempting to activate 2FA for user ID: {user.id}")
    try:
        data = request.get_json()
        totp_code = data['totp_code'] # Do not log the TOTP code
        
        # Check current status
        if user.mfa_enabled:
            logger.warning(f"2FA activation failed for user ID: {user.id}. 2FA is already activated.")
            raise http.RouteError("2FA already activated", http.ErrorCode.BAD_REQUEST)

        # Check the totp code
        if not user.verify_totp_code(totp_code):
            logger.warning(f"2FA activation failed for user ID: {user.id}. Invalid TOTP token provided.")
            raise http.RouteError("Invalid TOTP token", http.ErrorCode.UNAUTHORIZED)

        # Set flag to true
        user.mfa_enabled = True
        
        db.session.commit()
        logger.info(f"2FA successfully activated for user ID: {user.id}.")
        return jsonify({"message": "2FA activated successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"2FA activation failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during 2FA activation for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/2fa/status", methods=["GET"])
@login_required
def get_2fa_status():
    user: User = current_user
    logger.info(f"Attempting to retrieve 2FA status for user ID: {user.id}")
    try:
        # Return 2FA status
        status = {"enabled": user.mfa_enabled}
        logger.info(f"2FA status for user ID: {user.id} is: {status['enabled']}.")
        return jsonify(status), http.SuccessCode.OK.value
    except Exception as e:
        logger.error(f"An unexpected error occurred while retrieving 2FA status for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@account_bp.route("/2fa/disable", methods=["POST"])
@login_required
def disable_2fa():
    user: User = current_user
    logger.info(f"Attempting to disable 2FA for user ID: {user.id}")
    try:
        # Check current status
        if not user.mfa_enabled:
            logger.warning(f"2FA disable failed for user ID: {user.id}. 2FA is not currently enabled.")
            raise http.RouteError("2FA not set up", http.ErrorCode.BAD_REQUEST)

        # Set flag to false. The old secret does not need to be removed
        user.mfa_enabled = False
        db.session.commit()
        logger.info(f"2FA successfully disabled for user ID: {user.id}.")
        return jsonify({"message": "2FA disabled successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"2FA disable failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during 2FA disable for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value