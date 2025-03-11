from sqlalchemy import Integer, VARCHAR, Text, ForeignKey, UniqueConstraint, BigInteger
from sqlalchemy.orm import mapped_column
from app import db

class VaultEntry(db.Model):
    
    __tablename__ = 'vault_entry'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'))
    timestamp = mapped_column(BigInteger)  # Entry creation timestamp, provided by the client
    title = mapped_column(VARCHAR(255))
    url = mapped_column(VARCHAR(255), nullable=True)    # Plaintext
    encrypted_username = mapped_column(VARCHAR(255), nullable=True) # Encrypted and base64 encoded
    encrypted_password = mapped_column(VARCHAR(255), nullable=True) # Encrypted and base64 encoded
    notes = mapped_column(Text, nullable=True)  # Plaintext

    __table_args__ = (
        # An individual user can't have multiple entries with the same title or the same timestamp
        UniqueConstraint('user_id', 'title', name='unique_user_title'),
        UniqueConstraint('user_id', 'timestamp', name='unique_user_timestamp'),
    )

    # Dictionary containing only the information needed in the frontend
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'title': self.title,
            'url': self.url,
            'encrypted_username': self.encrypted_username,
            'encrypted_password': self.encrypted_password,
            'notes': self.notes
        }