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
        from app.util import security, get_now_timestamp  # Required utilities
        from app.routes import vault_bp, auth_bp, account_bp, admin_control_bp  # Route blueprints
        from app.views import AdminHomeView, UserModelView, KeyChainModelView, VaultEntryModelView, OTPModelView    # ModelViews
        
        # Init the kdf and fernet components
        if not app.config.get('FERNET_KEY', False) or not app.config.get('KDF_SECRET', False):
            raise ValueError('FERNET_KEY or KDF_SECRET not set in config')
        fernet_key, kdf_secret = str(app.config['FERNET_KEY']), str(app.config['KDF_SECRET'])
        security.fernet.init(fernet_key.encode())
        security.kdf.init(kdf_secret.encode())
        
        # Create all tables
        db.create_all()
        
        # Create the admin user if not in testing mode``
        if not app.config.get('TESTING', False):
            email = app.config.get('ADMIN_EMAIL', 'admin'),
            password = app.config.get('ADMIN_PASSWORD', 'admin')
            try:
                # Check if an admin with the given email already exists
                admin = models.User.query.filter_by(email=email).first()
                if admin:
                    print(f'Admin already exists with email: {email}')
                else:
                    # Create a new user
                    admin = models.User(
                        email=email, 
                        hashed_password=security.hasher.hash(password), 
                        is_admin=True,  # Make it an admin
                        created_at=get_now_timestamp()
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print(f'Admin created with email: {email}')
            except Exception as e:
                db.session.rollback()
                print(f'Error creating admin: {str(e)}')
        
        # Register all blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(vault_bp, url_prefix='/entries')
        app.register_blueprint(account_bp, url_prefix='/account')
        app.register_blueprint(admin_control_bp, url_prefix='/admin')
        
        # Define Admin dashboard with ModelViews
        app_admin = Admin(app, name='VaultBerry Admin', template_mode='bootstrap3', index_view=AdminHomeView())
        app_admin.add_view(UserModelView(models.User, db.session, category='Tables'))
        app_admin.add_view(KeyChainModelView(models.KeyChain, db.session, category='Tables'))
        app_admin.add_view(VaultEntryModelView(models.VaultEntry, db.session, category='Tables'))
        app_admin.add_view(OTPModelView(models.OneTimePassword, db.session, category='Tables'))
        app_admin.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))
        
    return app