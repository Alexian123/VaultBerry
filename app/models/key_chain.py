from sqlalchemy import Integer, VARCHAR
from sqlalchemy.orm import mapped_column
from app import db

class KeyChain(db.Model):
    __tablename__ = 'key_chain'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    salt = mapped_column(VARCHAR(24))   # Base64 encoded
    vault_key = mapped_column(VARCHAR(255)) # Encrypted and Base64 encoded
    recovery_key = mapped_column(VARCHAR(255))  # Encrypted and Base64 encoded

    def to_dict(self):
        return {
            'salt': self.salt,
            'vault_key': self.vault_key,
            'recovery_key': self.recovery_key
        }