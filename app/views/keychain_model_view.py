from app.views import AdminModelView

class KeyChainModelView(AdminModelView):
    column_list = (
        'id',
        'salt',
        'vault_key',
        'recovery_key'
    )