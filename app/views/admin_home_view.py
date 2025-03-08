from flask_admin import AdminIndexView, expose
from flask_login import current_user
from app.util import admin_utils

class AdminHomeView(AdminIndexView):

    @expose('/')
    @admin_utils.admin_required
    def index(self):
        return self.render('admin_home.html', admin_email=current_user.email)
