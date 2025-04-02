from app.views import AdminModelView

class UserModelView(AdminModelView):
    column_list = (
        "id",
        "is_admin",
        "mfa_enabled",
        "email",
        "first_name",
        "last_name",
        "created_at"
    )