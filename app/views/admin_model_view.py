from flask_admin.contrib.sqla import ModelView
from flask_login import login_required
from flask import redirect, url_for
from app.util import admin_required

class AdminModelView(ModelView):
    
    can_create = False
    can_edit = False
    can_delete = False
    
    @login_required
    @admin_required
    def is_accessible(self):
        return True