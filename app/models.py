from sqlalchemy import Integer, VARCHAR, Text, ForeignKey
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255) )
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class VaultEntry(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey('user.id'))
    title = mapped_column(VARCHAR(255))
    url = mapped_column(VARCHAR(255), nullable=True)
    encrypted_username = mapped_column(VARCHAR(255), nullable=True)
    encrypted_password = mapped_column(VARCHAR(255), nullable=True)
    notes = mapped_column(Text, nullable=True)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'title': self.title,
            'url': self.url,
            'encrypted_username': self.encrypted_username,
            'encrypted_password': self.encrypted_password,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<VaultEntry {self.title} for User {self.user_id}>'
