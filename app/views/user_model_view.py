from app.views import AdminModelView

class UserModelView(AdminModelView):
    column_list = (
        'id',
        'keychain_id',
        'email',
        'first_name',
        'last_name',
        'is_admin',
        'created_at'
    )