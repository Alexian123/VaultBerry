from sqlalchemy import Integer, VARCHAR, Text, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import mapped_column
from app import db

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
    
    def to_dict_full(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'title': self.title,
            'url': self.url,
            'encrypted_username': self.encrypted_username,
            'encrypted_password': self.encrypted_password,
            'notes': self.notes
        }