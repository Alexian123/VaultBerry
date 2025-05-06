from app.views import AdminModelView

class VaultEntryModelView(AdminModelView):
    column_list = (
        "id",
        "user_id",
        "last_modified",
        "title",
        "url",
        "notes"
    )