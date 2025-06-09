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
    logger.info(f"Attempting to retrieve all vault entry details for user ID: {user.id}")
    try:
        # Fetch all entry details for the current user
        entries = [entry.to_detailed_dict() for entry in user.entries]
        logger.info(f"Successfully retrieved {len(entries)} vault entry details for user ID: {user.id}")
        return jsonify(entries), http.SuccessCode.OK.value
    except Exception as e:
        logger.error(f"An unexpected error occurred while retrieving all vault entry details for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    

@vault_bp.route("/previews", methods=["GET"])
@login_required
def get_all_vault_entry_previews():
    user: User = current_user
    logger.info(f"Attempting to retrieve all vault entry previews for user ID: {user.id}")
    try:
        # Fetch all the entry previews for the current user
        previews = [entry.to_preview_dict() for entry in user.entries]
        logger.info(f"Successfully retrieved {len(previews)} vault entry previews for user ID: {user.id}")
        return jsonify(previews), http.SuccessCode.OK.value
    except Exception as e:
        logger.error(f"An unexpected error occurred while retrieving all vault entry previews for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value
    
    
@vault_bp.route("/details/<int:id>", methods=["GET"])
@login_required
def get_vault_entry_details(id: int):
    user: User = current_user
    logger.info(f"Attempting to retrieve vault entry details for entry ID: {id} for user ID: {user.id}")
    try:
        # Find the entry
        entry: VaultEntry = VaultEntry.query.filter_by(user_id=user.id).filter_by(id=id).first()
        
        # Check if the entry exists
        if entry is None:
            logger.warning(f"Vault entry details retrieval failed: Entry ID {id} not found for user ID: {user.id}")
            raise http.RouteError("Entry not found", http.ErrorCode.NOT_FOUND)
        
        # Return the entry
        logger.info(f"Successfully retrieved vault entry details for entry ID: {id} for user ID: {user.id}")
        return jsonify(entry.to_detailed_dict()), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"Vault entry details retrieval failed for entry ID: {id} for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        logger.error(f"An unexpected error occurred while retrieving vault entry details for entry ID: {id} for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

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
        logger.info(f"Attempting to search vault entries for user ID: {user.id} with keywords: {keywords}")
        
        # Check if keywords were provided
        if not keywords:
            logger.warning(f"Vault search failed for user ID: {user.id}: No keywords provided.")
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
        logger.info(f"Successfully found {len(entries)} vault entries matching keywords for user ID: {user.id}.")
        return jsonify([entry.to_detailed_dict() for entry in entries]), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"Vault search failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        logger.error(f"An unexpected error occurred during vault search for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/add", methods=["POST"])
@login_required
def add_vault_entry():
    user: User = current_user
    try:  
        data = request.get_json()
        entry_title = data["title"]
        logger.info(f"Attempting to add new vault entry with title '{entry_title}' for user ID: {user.id}")
        
        # Check if an entry with the given title already exists
        existing_entry = VaultEntry.query.filter_by(user_id=user.id).filter_by(title=entry_title).first()
        if existing_entry:
            logger.warning(f"Add vault entry failed for user ID: {user.id}. An entry with title '{entry_title}' already exists.")
            raise http.RouteError("An entry with this title already exists for this user", http.ErrorCode.CONFLICT)

        # Create the new entry
        new_entry = VaultEntry(
            user_id=user.id,
            last_modified=time.get_now_timestamp(),
            title=entry_title,
            url=data.get("url"),
            notes=data.get("notes")
        )
        
        # Set the encrypted fields
        new_entry.set_encrypted_fields(data.get("encrypted_username"), data.get("encrypted_password"))

        # Add the new entry to the database
        db.session.add(new_entry)
        db.session.commit()
        logger.info(f"New vault entry '{entry_title}' added successfully for user ID: {user.id}.")

        # Return the new entry preview
        return jsonify(new_entry.to_preview_dict()), http.SuccessCode.CREATED.value
    except http.RouteError as e:
        logger.warning(f"Add vault entry failed for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during adding vault entry for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/update/<int:id>", methods=["PATCH"])
@login_required
def update_vault_entry(id: int):
    data = request.json
    user: User = current_user
    logger.info(f"Attempting to update vault entry ID: {id} for user ID: {user.id}")
    try:
        # Find the entry to be updated by its id
        entry: VaultEntry = VaultEntry.query.filter_by(user_id=user.id).filter_by(id=id).first()
        if entry is None:
            logger.warning(f"Update vault entry failed: Entry ID {id} not found for user ID: {user.id}")
            raise http.RouteError("Entry not found", http.ErrorCode.NOT_FOUND)

        # Update the plaintext fields
        entry.last_modified = time.get_now_timestamp()
        entry.title = data["title"]
        entry.url = data.get("url", entry.url)
        entry.notes = data.get("notes", entry.notes)
        logger.debug(f"Plaintext fields updated for vault entry ID: {id} (user ID: {user.id}).")
        
        # Update the encrypted fields, if present
        new_encrypted_username = data.get("encrypted_username", None)
        new_encrypted_password = data.get("encrypted_password", None)
        entry.set_encrypted_fields(new_encrypted_username, new_encrypted_password)
        logger.debug(f"Encrypted fields updated for vault entry ID: {id} (user ID: {user.id}).")

        # If reencrypting, calculate the remaining number of entries left to patch
        entries_left = session.get(f"{user.id}_entries_left", 0)
        entries_left -= 1

        # Commit if this was the last entry to patch
        if entries_left <= 0:
            if entries_left == 0:  # Last entry for reencryption process
                logger.info(f"Re-encryption complete for user ID: {user.id}. Last entry patched: {id}. Total entries: {len(user.entries)}")
                del session[f"{user.id}_entries_left"]
            db.session.commit()
            logger.info(f"Vault entry ID: {id} updated successfully for user ID: {user.id}.")
        else:
            session[f"{user.id}_entries_left"] = entries_left  # Save the number of remining entries
            db.session.flush()
            logger.info(f"Vault entry ID: {id} patched for user ID: {user.id}. {entries_left} entries remaining for re-encryption.")
        
        return jsonify({"message": "Entry updated successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"Update vault entry failed for entry ID: {id} for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.error_code.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during updating vault entry ID: {id} for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value

@vault_bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_vault_entry(id: int):
    user: User = current_user
    logger.info(f"Attempting to delete vault entry ID: {id} for user ID: {user.id}")
    try:
        # Find the entry to be deleted by its ID
        entry = VaultEntry.query.filter_by(user_id=user.id).filter_by(id=id).first()
        if entry is None:
            logger.warning(f"Delete vault entry failed: Entry ID {id} not found for user ID: {user.id}")
            raise http.RouteError("Entry not found", http.ErrorCode.NOT_FOUND)

        # Delete the entry
        db.session.delete(entry)
        db.session.commit()
        logger.info(f"Vault entry ID: {id} successfully deleted for user ID: {user.id}.")

        return jsonify({"message": "Entry deleted successfully"}), http.SuccessCode.OK.value
    except http.RouteError as e:
        logger.warning(f"Delete vault entry failed for entry ID: {id} for user ID: {user.id}. Error: {e.error_code.name} - {str(e)}")
        return jsonify({"error": str(e)}), e.ErrorCode.value
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred during deleting vault entry ID: {id} for user ID: {user.id}. Error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), http.ErrorCode.INTERNAL_SERVER_ERROR.value