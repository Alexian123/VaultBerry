from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config):
    app = Flask(__name__)

    if config:
        app.config.from_object(config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app import routes, models
        from app.routes import auth_bp
        app.register_blueprint(auth_bp)

    return app