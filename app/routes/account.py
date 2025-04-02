from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import pyotp
import qrcode
import io
import base64
from app.models import User, Secret
from app import db, scram

account_bp = Blueprint("account", __name__)

@account_bp.route("", methods=["GET"])
@login_required
def get_account_info():
    user: User = current_user
    try:
        # The Account Info for the current user
        return jsonify(user.account_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@account_bp.route("", methods=["PATCH"])
@login_required
def update_account_info():
    data = request.json
    user: User = current_user
    try:
        # Find user by email
        existing_user: User = User.query.filter_by(email=data["email"]).first()
        if existing_user is not None and existing_user.id != user.id:
            return jsonify({"error": "Email associated with an existing account"}), 400

        # Update the user
        user.email = data["email"]
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        db.session.commit()

        return jsonify({"message": "Account updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@account_bp.route("", methods=["DELETE"])
@login_required
def delete_account():
    try:
        # Check if the keychain for the current user exists
        user: User = current_user
        if user.keychain is None:
            return jsonify({"error": "Inexistent keychain"}), 400

        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Account deleted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@account_bp.route("/password", methods=["PATCH"])
@login_required
def change_password():
    password_data = request.json["passwords"]
    keychain_data = request.json["keychain"]
    user: User = current_user
    try:
        # Check if the keychain exists
        if user.keychain is None:
            return jsonify({"error": "Inexistent keychain"}), 400
        
        # Update the keychain
        user.keychain.salt = keychain_data["salt"]
        user.keychain.vault_key = keychain_data["vault_key"]
        user.keychain.recovery_key = keychain_data["recovery_key"]
        
        # Update scram auth info for regular password
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(password_data["regular_password"])
        stored_key_secret: Secret = next((s for s in user.secrets if s.name == "SCRAM Stored Key"), None)
        server_key_secret: Secret = next((s for s in user.secrets if s.name == "SCRAM Server Key"), None)
        if stored_key_secret is None or server_key_secret is None:
            raise Exception("Missing scram secret")
        stored_key_secret.set_secret(stored_key)
        stored_key_secret.salt = salt
        stored_key_secret.iteration_count = iteration_count
        server_key_secret.set_secret(server_key)
        server_key_secret.salt = salt
        server_key_secret.iteration_count = iteration_count
        
        # Update scram auth info for recovery password
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(password_data["recovery_password"])
        stored_recovery_key_secret: Secret = next((s for s in user.secrets if s.name == "SCRAM Stored Key Recovery"), None)
        server_recovery_key_secret: Secret = next((s for s in user.secrets if s.name == "SCRAM Server Key Recovery"), None)
        if stored_recovery_key_secret is None or server_recovery_key_secret is None:
            raise Exception("Missing scram recovery secret")
        stored_recovery_key_secret.set_secret(stored_key)
        stored_recovery_key_secret.salt = salt
        stored_recovery_key_secret.iteration_count = iteration_count
        server_recovery_key_secret.set_secret(server_key)
        server_recovery_key_secret.salt = salt
        server_recovery_key_secret.iteration_count = iteration_count

        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@account_bp.route("/2fa/setup", methods=["POST"])
@login_required
def setup_2fa():
    user: User = current_user
    try:
        # Check if secret exists
        if user.mfa_enabled:
            return jsonify({"error": "2FA already set up"}), 400

        # Generate TOTP secret
        secret = pyotp.random_base32()

        # Encrypt and store
        user.set_totp_secret(secret)
        db.session.commit()

        # Generate a provisioning URI
        derived_key = user.get_totp_secret()
        provisioning_uri = pyotp.totp.TOTP(derived_key).provisioning_uri(
            name=user.email, issuer_name="VaultBerry"
        )

        # Generate a QR code
        qr = qrcode.make(provisioning_uri)
        buffered = io.BytesIO()
        qr.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({"provisioning_uri": provisioning_uri, "qrcode": img_str}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@account_bp.route("/2fa/status", methods=["GET"])
@login_required
def get_2fa_status():
    user: User = current_user
    try:
        # Return 2FA status
        return jsonify({"enabled": user.mfa_enabled}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@account_bp.route("/2fa/disable", methods=["POST"])
@login_required
def disable_2fa():
    user: User = current_user
    try:
        # Check current status
        if not user.mfa_enabled:
            return jsonify({"error": "2FA not set up"}), 400

        # Set flag to false. The old secret does not need to be removed
        user.mfa_enabled = False
        db.session.commit()
        return jsonify({"message": "2FA disabled successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400