from app.views import AdminModelView

class UserModelView(AdminModelView):
    column_list = (
        'id',
        'email',
        'first_name',
        'last_name',
        'is_admin'
    )