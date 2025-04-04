from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import User
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
    user: User = current_user
    try:
        data = request.get_json()
        
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
    user: User = current_user
    try:
        # Safety check: user must not be admin
        if user.is_admin():
            return jsonify({"error": "Cannot delete admin user"}), 400

        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@account_bp.route("/password", methods=["PATCH"])
@login_required
def change_password():
    user: User = current_user
    try:
        data = request.get_json()
        
        # Update the vault key secret
        user.set_vault_key_secret(data["vault_key"], data["salt"])
        
        # Update the SCRAM auth info
        salt, stored_key, server_key, iteration_count = scram.make_auth_info(data["password"])
        user.set_scram_auth_info(salt, stored_key, server_key, iteration_count)

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

        # Generate and save a new TOTP secret
        provisioning_uri, img_str = user.generate_totp_secret()
        db.session.commit()

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