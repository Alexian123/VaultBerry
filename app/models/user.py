from sqlalchemy import Integer, VARCHAR, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    keychain_id = mapped_column(Integer, ForeignKey('key_chain.id'), unique=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255))
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)
    is_admin = mapped_column(Boolean, default=False)

    def to_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
    
    def to_dict_full(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin
        }