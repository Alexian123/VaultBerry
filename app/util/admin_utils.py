from functools import wraps
from flask_login import current_user
from flask import abort, redirect, url_for
from app.models import User
from app.util import generate_password_hash
from app import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_control.admin_login')) # Redirect to login page
        if not current_user.is_admin:
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

def create_admin_user(email, password):
    try:
        admin = User.query.filter_by(email=email).first()
        if admin:
            print(f'Admin already exists with email: {email}')
            return
        
        admin = User(email=email, hashed_password=generate_password_hash(password), is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print(f'Admin created with email: {email}')
        return admin
    except Exception as e:
        db.session.rollback()
        print(f'Error creating admin: {str(e)}')