from flask import Blueprint, jsonify, request, session
from flask_login import current_user, login_required
from sqlalchemy import or_
from typing import List
from app.models import User, VaultEntry
from app.util import http, time
from app import db, logger

vault_bp = Blueprint("vault", __name__)

@vault_bp.route("/details", methods=["GET"])
@login_required
def get_all_vault_entry_details():
    user: User = current_user
    try:
        # Fetch all entry details for the current user
        return jsonify([entry.to_detailed_dict() for entry in user.entries]), http.SuccessCode.OK.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    

@vault_bp.route("/previews", methods=["GET"])
@login_required
def get_all_vault_entry_previews():
    user: User = current_user
    try:
        # Fetch all the entry previews for the current user
        return jsonify([entry.to_preview_dict() for entry in user.entries]), http.SuccessCode.OK.value
    except Exception as e:
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    
    
@vault_bp.route("/details/<int:id>", methods=["GET"])
@login_required
def get_vault_entry_details(id: int):
    user: User = current_user
    try:
        # Find the entry
        entry: VaultEntry = VaultEntry.query.filter_by(user_id=user.id).filter_by(id=id).first()
        
        # Check if the entry exists
        if entry is None:
            raise http.RouteError("Entry not found", http.ErrorCode.NOT_FOUND)
        
        # Return the entry
        return jsonify(entry.to_detailed_dict()), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        return jsonify({"error", str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/search", methods=["POST"])
@login_required
def search_vault_entries():
    """
    Retrieves vault entries for a specific user that match any of the keywords
    in the title, url, or notes.
    """
    user: User = current_user
    try:
        data = request.get_json()
        keywords = data["keywords"]
        
        # Check if keywords were provided
        if not keywords:
            raise http.RouteError("No keywords provided", http.ErrorCode.BAD_REQUEST)
        
        # Compute search conditions
        search_conditions = []
        for keyword in keywords:
            search_term = f"%{keyword}%"
            search_conditions.append(VaultEntry.title.ilike(search_term))
            search_conditions.append(VaultEntry.url.ilike(search_term))
            search_conditions.append(VaultEntry.notes.ilike(search_term))
        combined_conditions = or_(*search_conditions)
        
        # Query vault entries
        entries: List[VaultEntry] = VaultEntry.query.filter_by(user_id=user.id).filter(combined_conditions).all()
        return jsonify([entry.to_detailed_dict() for entry in entries]), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        return jsonify({"error", str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/add", methods=["POST"])
@login_required
def add_vault_entry():
    user: User = current_user
    try:   
        data = request.get_json()
        
        # Check if an entry with the given title already exists
        existing_entry = VaultEntry.query.filter_by(user_id=user.id).filter_by(title=data["title"]).first()
        if existing_entry:
            raise http.RouteError("An entry with this title already exists for this user", http.ErrorCode.CONFLICT)

        # Create the new entry
        new_entry = VaultEntry(
            user_id=user.id,
            last_modified=time.get_now_timestamp(),
            title=data["title"],
            url=data.get("url"),
            notes=data.get("notes")
        )
        
        # Set the encrypted fields
        new_entry.set_encrypted_fields(data.get("encrypted_username"), data.get("encrypted_password"))

        # Add the new entry to the database
        db.session.add(new_entry)
        db.session.commit()

        # Return the new entry preview
        return jsonify(new_entry.to_preview_dict()), http.SuccessCode.CREATED.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/update/<int:id>", methods=["PATCH"])
@login_required
def update_vault_entry(id: int):
    data = request.json
    user: User = current_user
    try:
        # Find the entry to be updated by its id
        entry: VaultEntry = VaultEntry.query.filter_by(user_id=user.id).filter_by(id=id).first()
        if entry is None:
            raise http.RouteError("Entry not found", http.ErrorCode.NOT_FOUND)

        # Update the plaintext fields
        entry.last_modified = time.get_now_timestamp()
        entry.title = data["title"]
        entry.url = data.get("url", entry.url)
        entry.notes = data.get("notes", entry.notes)
        
        # Update the encrypted fields, if present
        new_encrypted_username = data.get("encrypted_username", None)
        new_encrypted_password = data.get("encrypted_password", None)
        entry.set_encrypted_fields(new_encrypted_username, new_encrypted_password)

        # If reencrypting, calculate the remaining number of entries left to patch
        entries_left = session.get(f"{user.id}_entries_left", 0)
        entries_left -= 1

        # Commit if this was the last entry to patch
        if entries_left <= 0:
            if entries_left == 0:   # Last entry for reencryption process
                del session[f"{user.id}_entries_left"]
                logger.info(f"Patched entry {len(user.entries)}/{len(user.entries)}")
            db.session.commit()
        else:
            session[f"{user.id}_entries_left"] = entries_left   # Save the number of remining entries
            db.session.flush()
            logger.info(f"Patched entry {len(user.entries) - entries_left}/{len(user.entries)}")
        
        return jsonify({"message": "Entry updated successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_vault_entry(id: int):
    user: User = current_user
    try:
        # Find the entry to be deleted by its timestamp
        entry = VaultEntry.query.filter_by(user_id=user.id).filter_by(id=id).first()
        if entry is None:
            raise http.RouteError("Entry not found", http.ErrorCode.NOT_FOUND)

        # Delete the entry
        db.session.delete(entry)
        db.session.commit()

        return jsonify({"message": "Entry deleted successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value