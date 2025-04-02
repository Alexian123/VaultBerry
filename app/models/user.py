from sqlalchemy import Integer, String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from flask_login import UserMixin
import base64
from typing import TYPE_CHECKING
from app import db, scram
from app.util import security, get_now_timestamp

if TYPE_CHECKING:
    from .secret import Secret
    from .one_time_password import OneTimePassword
    from .key_chain import KeyChain
    from .vault_entry import VaultEntry

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Flags
    is_admin: MappedColumn[bool] = mapped_column(Boolean, default=False)
    mfa_enabled: MappedColumn[bool] = mapped_column(Boolean, default=False)
    
    # Account
    email: MappedColumn[str] = mapped_column(String(255), unique=True)
    first_name: MappedColumn[str] = mapped_column(String(255), nullable=True)
    last_name: MappedColumn[str] = mapped_column(String(255), nullable=True)
    created_at: MappedColumn[int] = mapped_column(BigInteger)
    
    # Credentials
    secrets: Mapped[list["Secret"]] = relationship("Secret", back_populates="user", cascade="all, delete")
    otps: Mapped[list["OneTimePassword"]] = relationship("OneTimePassword", back_populates="user", cascade="all, delete")
    
    # Vault
    keychain: Mapped["KeyChain"] = relationship("KeyChain", back_populates="user", cascade="all, delete")
    entries: Mapped[list["VaultEntry"]] = relationship("VaultEntry", back_populates="user", cascade="all, delete")

    def account_dict(self):
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at
        }
        
    def set_totp_secret(self, secret: str):
        """Derives, encrypts, and stores the TOTP secret.

        Args:
            secret (str): The TOTP secret
        """
        salt = security.generator.random_bytes(16)
        derived_key = security.kdf.derive_key(secret.encode(), salt)
        totp_secret: Secret = next((s for s in self.secrets if s.name == "TOTP"), None)
        if totp_secret is None:
            raise Exception("Missing TOTP secret")
        totp_secret.salt = salt
        totp_secret.set_secret(derived_key)
        self.mfa_enabled = True
        
    def get_totp_secret(self):
        """Fetches and decrypts the TOTP secret

        Returns:
            str: The decrypted secret
        """
        totp_secret: Secret = next((s for s in self.secrets if s.name == "TOTP"), None)
        if totp_secret is None:
            return None
        derived_key = totp_secret.get_secret()
        return base64.b32encode(derived_key).decode("utf-8").rstrip("=")    # must use b32encode here for compatibility
    
    @classmethod
    def create_admin(cls, email: str, password: str):
        """Creates an admin user with the given email and password, if it doesn't exist.

        Args:
            email (str): The email for the admin user.
            password (str): The password for the admin user.

        Returns:
            User: The new or existing user on success, None on failure.
        """
        try:
            # Check if an admin user with the given email already exists
            admin_user = db.session.query(cls).filter_by(is_admin=True, email=email).first()
            if admin_user:
                return admin_user
            
            # Create a new admin user
            admin_user = cls(
                email=email,
                first_name="Admin",
                last_name="User",
                is_admin=True,
                created_at=get_now_timestamp()
            )
            db.session.add(admin_user)
            db.session.flush()
            
            # Generate and store scram auth info for regular password
            from . import Secret
            salt, stored_key, server_key, iteration_count = scram.make_auth_info(password)
            stored_key_secret = Secret(user_id=admin_user.id, name="SCRAM Stored Key", salt=salt, iteration_count=iteration_count)
            stored_key_secret.set_secret(stored_key)
            db.session.add(stored_key_secret)
            server_key_secret = Secret(user_id=admin_user.id, name="SCRAM Server Key", salt=salt, iteration_count=iteration_count)
            server_key_secret.set_secret(server_key)
            db.session.add(server_key_secret)

            db.session.commit()  # Commit everything
            print(f"Admin with email '{email}' created successfully")
            return admin_user

        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")
            return None
        
    @staticmethod
    def get_auth_information(email: str) -> (tuple | None):
        try:
            user: User = User.query.filter_by(email=email).first()
            if not user:
                raise Exception("No user with this email exists")
            stored_key_secret: Secret = next((s for s in user.secrets if s.name == "SCRAM Stored Key"), None)
            server_key_secret: Secret = next((s for s in user.secrets if s.name == "SCRAM Server Key"), None)
            if not stored_key_secret or not server_key_secret:
                raise Exception("Missing scram secret")
            return stored_key_secret.salt, stored_key_secret.get_secret(), server_key_secret.get_secret(), stored_key_secret.iteration_count
        except Exception as e:
            return None