from sqlalchemy import Integer, String, ForeignKey, LargeBinary, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from typing import TYPE_CHECKING
from app import db
from app.util import security

if TYPE_CHECKING:
    from .user import User

class Secret(db.Model):
    __tablename__ = "secrets"
    
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(Enum("RECOVERY", "SCRAM_SERVER", "SCRAM_STORED", "VAULT_KEY", "VAULT_RECOVERY", "TOTP", name="secret_type", native_enum=True))
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    iteration_count: MappedColumn[int] = mapped_column(Integer, nullable=True)
    salt: MappedColumn[bytes] = mapped_column(LargeBinary, nullable=True)
    encrypted_secret: MappedColumn[bytes] = mapped_column(LargeBinary, nullable=True)
    
    user: Mapped["User"] = relationship("User", back_populates="secrets")
    
    __table_args__ = (
        UniqueConstraint("user_id", "type", name="_user_type_uc"),
    )
    
    def set_secret(self, secret: bytes):
        """Encrypt and store the secret.
        
        Args:
            secret (bytes): The secret to encrypt and store
        """
        self.encrypted_secret = security.fernet.encrypt(secret)
        
    def get_secret(self) -> bytes:
        """Decrypt and return the secret.
        
        Returns:
            bytes: The decrypted secret
        """
        return security.fernet.decrypt(self.encrypted_secret)
    
    @classmethod
    def create_default_secrets(cls, user_id: int):
        """Creates the empty required secrets.
        Must be called after db.session.flush() when creating a user.
        
        Args:
            user_id (int): The ID of the user who owns the secrets
        """
        db.session.add_all([
            cls(user_id=user_id, type="RECOVERY"), 
            cls(user_id=user_id, type="SCRAM_STORED"), 
            cls(user_id=user_id, type="SCRAM_SERVER"), 
            cls(user_id=user_id, type="VAULT_KEY"),
            cls(user_id=user_id, type="VAULT_RECOVERY"), 
            cls(user_id=user_id, type="TOTP")
        ])