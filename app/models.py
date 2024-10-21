from sqlalchemy import Integer, VARCHAR, ForeignKey
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    email = mapped_column(VARCHAR(255), unique=True, nullable=False)
    hashed_password = mapped_column(VARCHAR(255), unique=False, nullable=False)
    first_name = mapped_column(VARCHAR(255), unique=False, nullable=True)
    last_name = mapped_column(VARCHAR(255), unique=False, nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class VaultEntry(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = mapped_column(Integer, ForeignKey('user.id'), unique=False, nullable=False)
    name = mapped_column(VARCHAR(255), unique=False, nullable=False)
    url = mapped_column(VARCHAR(255), unique=False, nullable=True)
    encrypted_username = mapped_column(VARCHAR(255), unique=False, nullable=False)
    encrypted_password = mapped_column(VARCHAR(255), unique=False, nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'url': self.url,
            'encrypted_username': self.encrypted_username,
            'encrypted_password': self.encrypted_password
        }

    def __repr__(self):
        return f'<VaultEntry {self.url} for User {self.user_id}>'