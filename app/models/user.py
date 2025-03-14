from sqlalchemy import Integer, VARCHAR, ForeignKey, Boolean, BigInteger, LargeBinary
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
import base64
from app import db
from app.util import security

class User(db.Model, UserMixin):
    
    __tablename__ = 'users' # 'user' is reserved in PostgreSQL
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    keychain_id = mapped_column(Integer, ForeignKey('key_chain.id'), unique=True, nullable=True)    # Null only for the admin user
    
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255))
    hashed_recovery_password = mapped_column(VARCHAR(255))
    
    mfa_enabled = mapped_column(Boolean, default=False)
    encrypted_totp_derived_key = mapped_column(LargeBinary, nullable=True)
    totp_salt = mapped_column(LargeBinary, nullable=True)
    
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)
    
    is_admin = mapped_column(Boolean, default=False)
    
    created_at = mapped_column(BigInteger)
    
    # Dictionary containing only the account information
    def account_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
        
    def set_totp_secret(self, secret: str):
        """Derives, encrypts, and stores the TOTP secret.

        Args:
            secret (str): The TOTP secret
        """
        salt = security.generator.random_bytes(16)
        derived_key = security.kdf.derive_key(secret.encode(), salt)
        encrypted_derived_key = security.fernet.encrypt(derived_key)
        self.encrypted_totp_derived_key = encrypted_derived_key
        self.totp_salt = salt
        self.mfa_enabled = True
        
    def get_totp_secret(self):
        """Fetches and decrypts the TOTP secret

        Returns:
            str: The decrypted secret
        """
        if not self.encrypted_totp_derived_key or not self.totp_salt:
            return None
        derived_key = security.fernet.decrypt(self.encrypted_totp_derived_key)
        return base64.b32encode(derived_key).decode('utf-8').rstrip('=')