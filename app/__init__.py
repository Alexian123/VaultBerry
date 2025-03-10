from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_mail import Mail

# Components
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config):
    # Create flask app
    app = Flask(__name__, template_folder='../templates')

    # Set config
    app.config.from_object(config)
    
    # Init componentsd
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from app import models  # ORM Models
        from app.util import security_utils, admin_utils   # Required utilities
        from app.routes import vault_bp, auth_bp, account_bp, admin_control_bp  # Route blueprints
        from app.views import AdminHomeView, UserModelView, KeyChainModelView, VaultEntryModelView, OTPModelView    # ModelViews
        
        # Init the security manager (for totp secret encryption)
        if not app.config.get('FERNET_KEY', False) or not app.config.get('KDF_SECRET', False):
            raise ValueError('FERNET_KEY or KDF_SECRET not set in config')
        security_utils.manager.init(app.config.get('FERNET_KEY', ''), app.config.get('KDF_SECRET', ''))
        
        # Create all tables
        db.create_all()
        
        if not app.config.get('TESTING', False):
            # Create the admin user if not in testing mode
            admin_utils.create_admin_user(
                app.config.get('ADMIN_EMAIL', 'admin'),
                app.config.get('ADMIN_PASSWORD', 'admin')
            )
        
        # Register all blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(vault_bp, url_prefix='/entries')
        app.register_blueprint(account_bp, url_prefix='/account')
        app.register_blueprint(admin_control_bp, url_prefix='/admin')
        
        # Define Admin dashboard with ModelViews
        admin_utils = Admin(app, name='VaultBerry Admin', template_mode='bootstrap3', index_view=AdminHomeView())
        admin_utils.add_view(UserModelView(models.User, db.session, category='Tables'))
        admin_utils.add_view(KeyChainModelView(models.KeyChain, db.session, category='Tables'))
        admin_utils.add_view(VaultEntryModelView(models.VaultEntry, db.session, category='Tables'))
        admin_utils.add_view(OTPModelView(models.OneTimePassword, db.session, category='Tables'))
        admin_utils.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))
        
    return app