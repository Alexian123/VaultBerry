from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import User, VaultEntry
from app import db

vault_bp = Blueprint("vault", __name__)

@vault_bp.route("", methods=["GET"])
@login_required
def get_vault_entries():
    user: User = current_user
    try:
        # Fetch all the entries for the current user
        return jsonify([entry.to_dict() for entry in user.entries]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vault_bp.route("", methods=["POST"])
@login_required
def add_vault_entry():
    user: User = current_user
    try:   
        data = request.get_json()
        
        # Check if an entry with the given title already exists
        existing_entry = VaultEntry.query.filter_by(user_id=user.id).filter_by(title=data["title"]).first()
        if existing_entry:
            return jsonify({"error": "An entry with this title already exists for this user"}), 400

        # Create the new entry
        new_entry = VaultEntry(
            user_id=user.id,
            timestamp=data["timestamp"],
            title=data["title"],
            url=data.get("url"),
            notes=data.get("notes")
        )
        
        # Set the encrypted fields
        new_entry.set_encrypted_fields(data["encrypted_username"], data["encrypted_password"])

        # Add the new entry to the database
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Entry added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vault_bp.route("", methods=["PATCH"])
@login_required
def update_vault_entry():
    data = request.json
    user: User = current_user
    try:
        # Find the entry to be updated by its timestamp (unique per user)
        entry: VaultEntry = VaultEntry.query.filter_by(user_id=user.id).filter_by(timestamp=data["timestamp"]).first()
        if entry is None:
            return jsonify({"error": "Entry not found"}), 400

        # Update the plaintext fields
        entry.title = data["title"]
        entry.url = data.get("url", entry.url)
        entry.notes = data.get("notes", entry.notes)
        
        # Update the encrypted fields, if present
        new_encrypted_username = data.get("encrypted_username", None)
        new_encrypted_password = data.get("encrypted_password", None)
        entry.set_encrypted_fields(new_encrypted_username, new_encrypted_password)

        # Commit changes
        db.session.commit()
        
        return jsonify({"message": "Entry updated successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vault_bp.route("/<int:timestamp>", methods=["DELETE"])
@login_required
def delete_vault_entry(timestamp: int):
    user: User = current_user
    try:
        # Find the entry to be deleted by its timestamp
        entry = VaultEntry.query.filter_by(user_id=user.id).filter_by(timestamp=timestamp).first()
        if entry is None:
            return jsonify({"error": "Entry not found"}), 400

        # Delete the entry
        db.session.delete(entry)
        db.session.commit()

        return jsonify({"message": "Entry deleted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500