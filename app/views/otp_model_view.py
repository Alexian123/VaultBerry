from app.views import AdminModelView

class OTPModelView(AdminModelView):
    column_list = (
        'id',
        'user_id',
        'otp',
        'created_at',
        'expires_at',
        'used'
    )