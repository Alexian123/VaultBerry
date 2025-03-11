from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
import pyotp
import qrcode
import io
import base64
from app.models import User, KeyChain, VaultEntry, OneTimePassword
from app.util import security_utils
from app import db

account_bp = Blueprint('account', __name__)

@account_bp.route('', methods=['GET'])
@login_required
def get_account():
    try:
        # The Account Info for the current user
        return jsonify(current_user.account_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@account_bp.route('', methods=['PATCH'])
@login_required
def update_account():
    try:
        data = request.json

        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        if user and user.id != current_user.id:
            return jsonify({"error": "Email associated with an existing account"}), 400

        # Update the user
        current_user.email = data['email']
        current_user.first_name = data.get('first_name', current_user.first_name)
        current_user.last_name = data.get('last_name', current_user.last_name)
        db.session.commit()
        
        return jsonify({"message": "Account updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@account_bp.route('', methods=['DELETE'])
@login_required
def delete_account():
    try:
        # Delete the keychain for the current user
        keychain = KeyChain.query.filter_by(id=current_user.keychain_id).first()
        if not keychain:
            return jsonify({"error": "Inexistent keychain"}), 400
        db.session.delete(keychain)

        # Delete all entries for the current user
        entries = VaultEntry.query.filter_by(user_id=current_user.id).all()
        for entry in entries:
            db.session.delete(entry)

        # Delete all saved otp's for the current user
        otps = OneTimePassword.query.filter_by(user_id=current_user.id).all()
        for otp in otps:
            db.session.delete(otp)
        
        # Delete the user itself
        db.session.delete(current_user)
        db.session.commit()
        
        return jsonify({"message": "Account deleted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@account_bp.route('/password', methods=['PATCH'])
@login_required
def change_password():
    try:
        data = request.json
        password = data['regular_password']
        recovery_password = data['recovery_password']

        # Check if new password is different
        if security_utils.check_password_hash(current_user.hashed_password, password):
            return jsonify({"error": "The new password must be different from the old password"}), 400

        # Update the password and recovery password
        current_user.hashed_password = security_utils.generate_password_hash(password)
        current_user.hashed_recovery_password = security_utils.generate_password_hash(recovery_password)

        db.session.commit()
        return jsonify({"message": "Password changed successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@account_bp.route('/keychain', methods=['PUT'])
@login_required
def update_keychain():
    try:
        data = request.json

        # Find the keychain
        keychain = KeyChain.query.filter_by(id=current_user.keychain_id).first()
        if not keychain:
            return jsonify({"error": "Inexistent keychain"}), 400

        # Update the keychain
        keychain.salt = data['salt']
        keychain.vault_key = data['vault_key']
        keychain.recovery_key = data['recovery_key']

        db.session.commit()
        return jsonify({"message": "Keychain updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@account_bp.route('/2fa/setup', methods=['POST'])
@login_required
def setup_2fa():
    try:
        if current_user.mfa_enabled:  # Check if secret exists
            return jsonify({'error': '2FA already set up'}), 400
        
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Encrypt and store
        current_user.set_totp_secret(secret)
        db.session.commit()
        
        # Generate a provisioning URI
        derived_key = current_user.get_totp_secret()
        provisioning_uri = pyotp.totp.TOTP(derived_key).provisioning_uri(
            name=current_user.email, issuer_name="VaultBerry"
        )
        
        # Generate a QR code
        qr = qrcode.make(provisioning_uri)
        buffered = io.BytesIO()
        qr.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({'provisioning_uri': provisioning_uri, 'qrcode': img_str}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@account_bp.route('/2fa/status', methods=['GET'])
@login_required
def get_2fa_status():
    try:
        # Return flag
        return jsonify({'enabled': current_user.mfa_enabled}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@account_bp.route('/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    try:
        # Check current status
        if not current_user.mfa_enabled:
            return jsonify({'error': '2FA not set up'}), 400
        
        # Set flag to false. The old secret does not need to be removed
        current_user.mfa_enabled = False
        db.session.commit()
        
        return jsonify({'message': '2FA disabled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400