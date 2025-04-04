from app.views import AdminModelView

class UserModelView(AdminModelView):
    column_list = (
        "id",
        "role",
        "mfa_enabled",
        "email",
        "first_name",
        "last_name",
        "created_at"
    )