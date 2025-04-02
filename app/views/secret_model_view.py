from app.views import AdminModelView

class SecretModelView(AdminModelView):
    column_list = (
        "id",
        "user_id",
        "name"
    )