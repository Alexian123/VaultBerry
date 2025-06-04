from app.views import AdminModelView
from app.util import timestamp_as_datetime_string

class OTPModelView(AdminModelView):
    column_list = (
        "id",
        "user_id",
        "otp",
        "created_at",
        "expires_at",
        "used"
    )
    
    column_formatters = {
        "created_at": lambda view, context, model, name: timestamp_as_datetime_string(model.created_at),
        "expires_at": lambda view, context, model, name: timestamp_as_datetime_string(model.expires_at)
    }