from app.views import AdminModelView

class KeyChainModelView(AdminModelView):
    column_list = (
        "id",
        "user_id",
        "salt"
    )