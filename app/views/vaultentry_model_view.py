from app.views import AdminModelView

class VaultEntryModelView(AdminModelView):
    column_list = (
        'id',
        'user_id',
        'timestamp',
        'title',
        'url',
        'encrypted_username',
        'encrypted_password',
        'notes'
    )