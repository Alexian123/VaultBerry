from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import VaultEntry
from app import db

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('/entries', methods=['GET'])
@login_required
def get_vault_entries():
    try:
        entries = VaultEntry.query.filter_by(user_uuid=current_user.uuid).all()
        return jsonify({"entries": [entry.to_dict() for entry in entries]}), 200
    except Exception as e:
        return jsonify({"message": "Failed to retrieve entries", "error": str(e)}), 500


@vault_bp.route('/entries/add', methods=['POST'])
@login_required
def add_vault_entry():
    data = request.json

    try:
        existing_entry = VaultEntry.query.filter_by(user_uuid=current_user.uuid).filter_by(title=data['title']).first()
        if existing_entry:
            return jsonify({"message": "An entry with this title already exists for this user"}), 400

        new_entry = VaultEntry(
            user_uuid=current_user.uuid,
            title=data['title'],
            url=data.get('url'),
            encrypted_username=data['encrypted_username'],
            encrypted_password=data['encrypted_password'],
            notes=data.get('notes')
        )

        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Entry added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to add entry", "error": str(e)}), 500

@vault_bp.route('/entries/modify', methods=['POST'])
@login_required
def modify_vault_entry():
    data = request.json

    try:
        entry = VaultEntry.query.filter_by(user_uuid=current_user.uuid).filter_by(id=data['id']).first()
        if entry is None:
            return jsonify({"message": "No entry with this ID exists for this user"}), 400

        entry.title = data['title']
        entry.url = data.get('url')
        entry.encrypted_password = data.get('encrypted_password')
        entry.encrypted_username = data.get('encrypted_username')
        entry.notes = data.get('notes')

        db.session.commit()
        
        return jsonify({"message": "Entry modified successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to modify entry", "error": str(e)}), 500

@vault_bp.route('/entries/remove', methods=['POST'])
@login_required
def remove_vault_entry():
    data = request.json

    try:
        entry = VaultEntry.query.filter_by(user_uuid=current_user.uuid).filter_by(id=data['id']).first()
        if entry is None:
            return jsonify({"message": "No entry with this id exists for this user"}), 400

        db.session.delete(entry)
        db.session.commit()

        return jsonify({"message": "Entry removed successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to remove entry", "error": str(e)}), 500