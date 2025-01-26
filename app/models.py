from sqlalchemy import Integer, VARCHAR, Text, ForeignKey, UniqueConstraint, BigInteger, Boolean
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255))
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'fist_name': self.first_name,
            'last_name': self.last_name
        }

    def __repr__(self):
        return f'<User {self.email}>'

class KeyChain(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey('user.id'), unique=True)
    salt = mapped_column(VARCHAR(24))
    vault_key = mapped_column(VARCHAR(255))
    recovery_key = mapped_column(VARCHAR(255))

    def to_dict(self):
        return {
            'salt': self.salt,
            'vault_key': self.vault_key,
            'recovery_key': self.recovery_key
        }
class OneTimePassword(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, db.ForeignKey('user.id'))
    otp = mapped_column(VARCHAR(9), unique=True)
    expires_at = mapped_column(BigInteger)
    used = mapped_column(Boolean, default=False)
    
class VaultEntry(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey('user.id'))
    timestamp = mapped_column(BigInteger)
    title = mapped_column(VARCHAR(255))
    url = mapped_column(VARCHAR(255), nullable=True)
    encrypted_username = mapped_column(VARCHAR(255), nullable=True)
    encrypted_password = mapped_column(VARCHAR(255), nullable=True)
    notes = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='unique_user_title'),
        UniqueConstraint('user_id', 'timestamp', name='unique_user_timestamp'),
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
