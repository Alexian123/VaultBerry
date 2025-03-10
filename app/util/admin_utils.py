from functools import wraps
from flask_login import current_user
from flask import abort, redirect, url_for
from app.models import User
from app.util.security_utils import generate_password_hash
from app.util.time_utils import get_now_timestamp
from app import db

# Decorator to ensure the user is an authenticated admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_control.admin_login')) # Redirect to login page if not authenticated
        if not current_user.is_admin:
            abort(403) # Return 403 Forbidden if not an admin
        return f(*args, **kwargs)
    return decorated_function

def create_admin_user(email, password):
    """Create a new admin user.

    Args:
        email (str): Admin email address.
        password (str): Admin password.

    Returns:
        User: The newly created admin user.
    """
    try:
        # Check if an admin with the given email already exists
        admin = User.query.filter_by(email=email).first()
        if admin:
            print(f'Admin already exists with email: {email}')
            return
        
        # Create a new user
        admin = User(
            email=email, 
            hashed_password=generate_password_hash(password), 
            is_admin=True,  # Make it an admin
            created_at=get_now_timestamp()
        )
        db.session.add(admin)
        db.session.commit()
        print(f'Admin created with email: {email}')
        return admin
    except Exception as e:
        db.session.rollback()
        print(f'Error creating admin: {str(e)}')