from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import VaultEntry
from app import db

vault_bp = Blueprint('vault', __name__)

@vault_bp.route('', methods=['GET'])
@login_required
def get_vault_entries():
    try:
        # Fetch all the entries for the current user
        entries = VaultEntry.query.filter_by(user_id=current_user.id).all()
        return jsonify([entry.to_dict() for entry in entries]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vault_bp.route('', methods=['POST'])
@login_required
def add_vault_entry():
    try:
        data = request.json

        # Check if an entry with the given title already exists
        existing_entry = VaultEntry.query.filter_by(user_id=current_user.id).filter_by(title=data['title']).first()
        if existing_entry:
            return jsonify({"error": "An entry with this title already exists for this user"}), 400

        # Create the new entry
        new_entry = VaultEntry(
            user_id=current_user.id,
            timestamp=data['timestamp'],
            title=data['title'],
            url=data.get('url'),
            encrypted_username=data['encrypted_username'],
            encrypted_password=data['encrypted_password'],
            notes=data.get('notes')
        )

        # Add the new entry to the database
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Entry added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vault_bp.route('', methods=['PATCH'])
@login_required
def update_vault_entry():
    try:
        data = request.json

        # Find the entry to be updated by its timestamp (unique per user)
        entry = VaultEntry.query.filter_by(user_id=current_user.id).filter_by(timestamp=data['timestamp']).first()
        if entry is None:
            return jsonify({"error": "Entry not found"}), 400

        # Update the entry
        entry.title = data['title']
        entry.url = data.get('url', entry.url)
        entry.encrypted_password = data.get('encrypted_password', entry.encrypted_password)
        entry.encrypted_username = data.get('encrypted_username', entry.encrypted_username)
        entry.notes = data.get('notes', entry.notes)

        db.session.commit()
        
        return jsonify({"message": "Entry updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vault_bp.route('/<int:timestamp>', methods=['DELETE'])
@login_required
def delete_vault_entry(timestamp):
    try:
        # Find the entry to be deleted by its timestamp
        entry = VaultEntry.query.filter_by(user_id=current_user.id).filter_by(timestamp=timestamp).first()
        if entry is None:
            return jsonify({"error": "Entry not found"}), 400

        # Delete the entry
        db.session.delete(entry)
        db.session.commit()

        return jsonify({"message": "Entry deleted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500