from app.views import AdminModelView
from app.util import timestamp_as_datetime_string

class UserModelView(AdminModelView):
    column_list = (
        "id",
        "role",
        "is_activated",
        "verification_token",
        "token_expiration"
        "mfa_enabled",
        "email",
        "first_name",
        "last_name",
        "created_at"
    )
    
    column_formatters = {
        "created_at": lambda view, context, model, name: timestamp_as_datetime_string(model.created_at),
        "token_expiration": lambda view, context, model, name: timestamp_as_datetime_string(model.token_expiration)
    }