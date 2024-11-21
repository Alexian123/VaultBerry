from sqlalchemy import Integer, VARCHAR, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db
import uuid

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid = mapped_column(VARCHAR(36), default=lambda: str(uuid.uuid4()), unique=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255) )
    vault_key = mapped_column(VARCHAR(255))
    recovery_key = mapped_column(VARCHAR(255))
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'email': self.email,
            'vault_key': self.vault_key,
            'recovery_key': self.recovery_key,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class VaultEntry(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_uuid = mapped_column(VARCHAR(36), ForeignKey('user.uuid'))
    title = mapped_column(VARCHAR(255))
    url = mapped_column(VARCHAR(255), nullable=True)
    encrypted_username = mapped_column(VARCHAR(255), nullable=True)
    encrypted_password = mapped_column(VARCHAR(255), nullable=True)
    notes = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_uuid', 'title', name='unique_user_title'),
    )

    def to_dict(self):
        return {
            'title': self.title,
            'url': self.url,
            'encrypted_username': self.encrypted_username,
            'encrypted_password': self.encrypted_password,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<VaultEntry {self.title} for User {self.user_id}>'
