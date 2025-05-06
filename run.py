"""The entry point of the application"""
from app import create_app
from config import DevConfig

# Create an instance of the app with the development configuration
app = create_app(DevConfig)

# TODO: Use marshmallow for serializable objects