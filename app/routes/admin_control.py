from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user
from scramp import ScramClient
from app.models import User, Secret
from app.util import admin_required
from app import scram, logger

admin_control_bp = Blueprint("admin_control", __name__)

@admin_control_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    user: User = current_user
    if user and user.is_authenticated and user.is_admin():
        # Already logged in
        logger.info(f"Admin user {user.id} (email: {user.email}) is already logged in, redirecting to admin index.")
        return redirect(url_for("admin.index"))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password") # Do not log the password
        logger.info(f"Admin login attempt for email: {email}")
        try:
            # Find the user by email
            existing_user: User = User.query.filter_by(email=email).first()
            
            if existing_user is None:
                logger.warning(f"Admin login failed for email: {email} - User not found.")
                raise Exception("No user with this email exists.")
            elif not existing_user.is_admin():
                logger.warning(f"Admin login failed for email: {email} - User is not an admin.")
                raise Exception("User is not an admin.")

            # Create the SCRAM client and server
            client, server = ScramClient(['SCRAM-SHA-256'], email, password), scram.make_server(User.get_auth_information)
            logger.debug(f"SCRAM client and server created for admin login for email: {email}.")
            
            # Generate client first message
            client_first_message = client.get_client_first()
            
            # Get server first message
            server.set_client_first(client_first_message)
            server_first_message = server.get_server_first()
            
            # Get client final message
            client.set_server_first(server_first_message)
            client_final_message = client.get_client_final()
            
            # Get server final message
            server.set_client_final(client_final_message)
            server_final_message = server.get_server_final()
            
            # Check server final message
            client.set_server_final(server_final_message)
            
            # Access granted
            login_user(existing_user)
            logger.info(f"Admin user {existing_user.id} (email: {existing_user.email}) logged in successfully.")
            return redirect(url_for("admin.index"))
        except Exception as e:
            logger.error(f"Admin login failed for email: {email}. Error: {e}", exc_info=True)
            flash(str(e))
    
    # HTML Login form
    logger.debug("Rendering admin login page.")
    return render_template("admin_login.html")

@admin_control_bp.route("/logout", methods=["GET"])
@admin_required
def admin_logout():
    user_id = None
    user_email = None
    if current_user and current_user.is_authenticated:
        user_id = current_user.id
        user_email = current_user.email
    
    logout_user()
    logger.info(f"Admin user {user_id} (email: {user_email}) logged out successfully.")
    return redirect(url_for("admin.index"))