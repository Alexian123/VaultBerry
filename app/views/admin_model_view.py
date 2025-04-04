from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for
from flask_login import current_user

class AdminModelView(ModelView):
    
    can_create = False
    can_edit = False
    can_delete = False
    list_template = "admin_model_list.html"
    
    def is_accessible(self):
        if not current_user.is_authenticated or not current_user.is_admin():
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("admin_control.admin_login"))
    
    def get_model_name(self):
        return self.model.__name__