from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user
from scramp import ScramClient
from app.models import User, Secret
from app.util import admin_required
from app import scram

admin_control_bp = Blueprint("admin_control", __name__)

@admin_control_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    user: User = current_user
    if user and user.is_authenticated and user.is_admin():
        # Already logged in
        return redirect(url_for("admin.index"))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            # Find the user by email
            existing_user: User = User.query.filter_by(email=email).first()
            
            if existing_user is None:
                raise Exception("No user with this email exists.")
            elif not existing_user.is_admin():
                raise Exception("User is not an admin.")

            # Create the SCRAM client and server
            client, server = ScramClient(['SCRAM-SHA-256'], email, password), scram.make_server(User.get_auth_information)
            
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
            return redirect(url_for("admin.index"))
        except Exception as e:
            flash(str(e))
    
    # HTML Login form
    return render_template("admin_login.html")

@admin_control_bp.route("/logout", methods=["GET"])
@admin_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin.index"))