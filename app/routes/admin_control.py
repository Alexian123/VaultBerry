from flask import Blueprint, jsonify, request, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, current_user
from app.models import User
from app.util import check_password_hash, admin_required

admin_control_bp = Blueprint('admin_control', __name__)

@admin_control_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.index'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            if not user:
                flash("No user with this email exists.")
            elif not check_password_hash(user.hashed_password, password):
                flash("Invalid password.")
            elif not user.is_admin:
                flash("User is not an admin.")
            else: 
                login_user(user)
                return redirect(url_for('admin.index'))
        except Exception as e:
            return flash(str(e))
    
    return render_template('admin_login.html')

@admin_control_bp.route('/logout', methods=['GET'])
@admin_required
def admin_logout():
    logout_user()
    return render_template('admin_login.html')