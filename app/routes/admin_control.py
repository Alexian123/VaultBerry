from flask import Blueprint, jsonify, request, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.util import check_password_hash, admin_required
from app.config import BaseConfig
from app import db

admin_control_bp = Blueprint('admin_control', __name__)

@admin_control_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            email = BaseConfig.ADMIN_EMAIL
            password = request.form['password']

            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "No user with this email exists"}), 401

            if not check_password_hash(user.hashed_password, password):
                return jsonify({"error": "Invalid password"}), 401

            if not user.is_admin:
                return jsonify({"error": "User is not an admin"}), 403
            
            login_user(user)
            return redirect(url_for('admin.index'))
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template('admin_login.html')

@admin_control_bp.route('/logout', methods=['GET'])
@login_required
@admin_required
def admin_logout():
    try:    
        logout_user()
        return render_template('admin_login.html')
    except Exception as e:
        return jsonify({"error": str(e)}), 400