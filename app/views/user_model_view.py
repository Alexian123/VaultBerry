from app.views import AdminModelView
from app.util import time

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
    
    column_formatters = {
        "created_at": lambda view, context, model, name: time.timestamp_as_datetime_string(model.created_at)
    }