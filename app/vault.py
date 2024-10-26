from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import VaultEntry
from app import db

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/entries', methods=['GET'])
@login_required
def get_vault_entries():
    entries = VaultEntry.query.filter_by(user_id=current_user.id).all()
    return jsonify({"entries": [entry.to_dict() for entry in entries]})

@vault_bp.route('/entries', methods=['POST'])
@login_required
def add_vault_entry():
    data = request.json
    new_entry = VaultEntry(
        user_id=current_user.id,
        title=data['title'],
        url=data.get('url'),
        encrypted_username=data['encrypted_username'],
        encrypted_password=data['encrypted_password']
    )
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "Entry added successfully"}), 201