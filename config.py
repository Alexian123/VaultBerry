import os
from datetime import timedelta
from dotenv import load_dotenv

try:
    load_dotenv(dotenv_path=".env")
except Exception as e:
    print("Error loading environment file")

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "sessions"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    BASE_URL = os.environ.get("BASE_URL")
    
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")
    
    FERNET_KEY = os.environ.get("FERNET_KEY")
    KDF_SECRET = os.environ.get("KDF_SECRET")

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test key"
    TESTING = True