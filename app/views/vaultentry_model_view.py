from app.views import AdminModelView
from app.util import time

class VaultEntryModelView(AdminModelView):
    column_list = (
        "id",
        "user_id",
        "last_modified",
        "title",
        "url",
        "notes"
    )
    
    column_formatters = {
        "last_modified": lambda view, context, model, name: time.timestamp_as_datetime_string(model.last_modified)
    }
