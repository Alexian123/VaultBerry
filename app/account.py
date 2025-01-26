from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from app.models import User, KeyChain, VaultEntry
from app import db

account_bp = Blueprint('account', __name__)

BASE_URL = "/account"

@account_bp.route(BASE_URL, methods=['POST'])
@login_required
def update_account():
    try:
        data = request.json

        user = User.query.filter_by(email=data['email']).first()
        if user and user.id != current_user.id:
            return jsonify({"error": "Email already in use"}), 400

        current_user.email = data['email']
        current_user.hashed_password=generate_password_hash(data['password'])
        current_user.first_name = data.get('first_name')
        current_user.last_name = data.get('last_name')
        db.session.commit()
        return jsonify({"message": "Account updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@account_bp.route(BASE_URL, methods=['DELETE'])
@login_required
def delete_account():
    try:
        keychain = KeyChain.query.filter_by(user_id=current_user.id).first()
        if not keychain:
            return jsonify({"error": "Inexistent keychain"}), 400
        db.session.delete(keychain)

        entries = VaultEntry.query.filter_by(user_id=current_user.id).all()
        for entry in entries:
            db.session.delete(entry)
        
        db.session.delete(current_user)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@account_bp.route(f'{BASE_URL}/keychain', methods=['POST'])
@login_required
def update_keychain():
    try:
        data = request.json

        keychain = KeyChain.query.filter_by(user_id=current_user.id).first()
        if not keychain:
            return jsonify({"error": "Inexistent keychain"}), 400

        keychain.salt = data['salt']
        keychain.vault_key = data['vault_key']
        keychain.recovery_key = data['recovery_key']

        db.session.commit()
        return jsonify({"message": "Keychain updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400