from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config):
    app = Flask(__name__)

    app.config.from_object(config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    with app.app_context():
        from app import models
        from app.routes import vault_bp, auth_bp, account_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(vault_bp, url_prefix='/entries')
        app.register_blueprint(account_bp, url_prefix='/account')

    return app