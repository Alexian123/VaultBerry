from functools import wraps
from flask_login import current_user
from flask import abort, redirect, url_for

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