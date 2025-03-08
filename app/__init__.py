from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_mail import Mail

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config):
    app = Flask(__name__, template_folder='../templates')

    app.config.from_object(config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app import models
        from app.util import security_utils, admin_utils
        from app.routes import vault_bp, auth_bp, account_bp, admin_control_bp
        from app.views import AdminHomeView, UserModelView, KeyChainModelView, VaultEntryModelView, OTPModelView
        
        if not app.config.get('FERNET_KEY', False) or not app.config.get('KDF_SECRET', False):
            raise ValueError('FERNET_KEY or KDF_SECRET not set in config')
        security_utils.manager.init(app.config.get('FERNET_KEY', ''), app.config.get('KDF_SECRET', ''))
        
        db.create_all()
        
        if not app.config.get('TESTING', False):
            admin_utils.create_admin_user(
                app.config.get('ADMIN_EMAIL', 'admin'),
                app.config.get('ADMIN_PASSWORD', 'admin')
            )
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(vault_bp, url_prefix='/entries')
        app.register_blueprint(account_bp, url_prefix='/account')
        app.register_blueprint(admin_control_bp, url_prefix='/admin')
        
        admin_utils = Admin(app, name='VaultBerry Admin', template_mode='bootstrap3', index_view=AdminHomeView())
        admin_utils.add_view(UserModelView(models.User, db.session, category='Tables'))
        admin_utils.add_view(KeyChainModelView(models.KeyChain, db.session, category='Tables'))
        admin_utils.add_view(VaultEntryModelView(models.VaultEntry, db.session, category='Tables'))
        admin_utils.add_view(OTPModelView(models.OneTimePassword, db.session, category='Tables'))
        admin_utils.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))
        
    return app