import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_mail import Mail
from flask_session import Session
from scramp import ScramMechanism

# Logger Configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Components
logger: logging.Logger
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
sess = Session()
scram = ScramMechanism()

def create_app(config):
    # Create flask app
    app = Flask(__name__, template_folder="../templates")

    # Set config
    app.config.from_object(config)
    
    # Configure Session
    app.config["SESSION_SQLALCHEMY"] = db
    
    # Init components
    global logger
    logger = app.logger
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    if not app.config.get("TESTING", False): # Only use the server stored session when not testing
        sess.init_app(app)

    with app.app_context():
        from app import models  # ORM Models
        from app.util import security  # Required utilities
        from app.routes import vault_bp, auth_bp, account_bp, admin_control_bp  # Route blueprints
        from app.views import AdminHomeView, UserModelView, VaultEntryModelView, OTPModelView, SecretModelView    # ModelViews
        
        # Init the kdf and fernet components
        if app.config.get("FERNET_KEY") is None or app.config.get("KDF_SECRET") is None:
            raise ValueError("FERNET_KEY or KDF_SECRET not set in config")
        fernet_key, kdf_secret = str(app.config["FERNET_KEY"]), str(app.config["KDF_SECRET"])
        security.fernet.init(fernet_key.encode())
        security.kdf.init(kdf_secret.encode())
        
        # Create all tables
        db.create_all()
        
        # Create the admin user if not in testing mode
        if not app.config.get("TESTING", False):
            email = app.config.get("ADMIN_EMAIL", "admin")
            password = app.config.get("ADMIN_PASSWORD", "admin")
            models.User.create_admin(email, password)
        
        # Register all blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(vault_bp, url_prefix="/entries")
        app.register_blueprint(account_bp, url_prefix="/account")
        app.register_blueprint(admin_control_bp, url_prefix="/admin")
        
        # Define Admin dashboard with ModelViews
        app_admin = Admin(app, name="VaultBerry Admin", template_mode="bootstrap3", index_view=AdminHomeView())
        app_admin.add_view(UserModelView(models.User, db.session, category="Tables"))
        app_admin.add_view(SecretModelView(models.Secret, db.session, category="Tables"))
        app_admin.add_view(VaultEntryModelView(models.VaultEntry, db.session, category="Tables"))
        app_admin.add_view(OTPModelView(models.OneTimePassword, db.session, category="Tables"))
        app_admin.add_link(MenuLink(name="Logout", category="", url="/admin/logout"))
        
    return app
