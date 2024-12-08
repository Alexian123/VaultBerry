from sqlalchemy import Integer, VARCHAR, Text, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db
import uuid

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid = mapped_column(VARCHAR(36), default=lambda: str(uuid.uuid4()), unique=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255))
    salt = mapped_column(VARCHAR(24))
    vault_key = mapped_column(VARCHAR(255))
    recovery_key = mapped_column(VARCHAR(255))
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)

    def to_dict(self):
        return {
            'uuid': self.uuid,
            'email': self.email,
            'fist_name': self.first_name,
            'last_name': self.last_name
        }

    def __repr__(self):
        return f'<User {self.email}>'

class VaultEntry(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_uuid = mapped_column(VARCHAR(36), ForeignKey('user.uuid'))
    timestamp = mapped_column(BigInteger)
    title = mapped_column(VARCHAR(255))
    url = mapped_column(VARCHAR(255), nullable=True)
    encrypted_username = mapped_column(VARCHAR(255))
    encrypted_password = mapped_column(VARCHAR(255))
    notes = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_uuid', 'title', name='unique_user_title'),
    )

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'title': self.title,
            'url': self.url,
            'encrypted_username': self.encrypted_username,
            'encrypted_password': self.encrypted_password,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<VaultEntry {self.title} for User {self.user_id}>'
