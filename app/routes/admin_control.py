from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user
from app.models import User
from app.util import admin_utils, security_utils

admin_control_bp = Blueprint('admin_control', __name__)

@admin_control_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        # Akready logged in
        return redirect(url_for('admin.index'))
    
    if request.method == 'POST':
        try:
            # Read data from Login form
            email = request.form.get('email')
            password = request.form.get('password')
        
            # Find the user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash("No user with this email exists.")
            elif not security_utils.check_password_hash(user.hashed_password, password):
                flash("Invalid password.")
            elif not user.is_admin:
                flash("User is not an admin.")
            else: 
                # Access granted
                login_user(user)
                return redirect(url_for('admin.index'))
        except Exception as e:
            return flash(str(e))
    
    # HTML Login form
    return render_template('admin_login.html')

@admin_control_bp.route('/logout', methods=['GET'])
@admin_utils.admin_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.index'))