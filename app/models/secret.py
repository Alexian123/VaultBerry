from sqlalchemy import Integer, String, ForeignKey, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from typing import TYPE_CHECKING
from app import db
from app.util import security

if TYPE_CHECKING:
    from .user import User

class Secret(db.Model):
    __tablename__ = "secrets"
    
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name: MappedColumn[str] = mapped_column(String(255))
    iteration_count: MappedColumn[int] = mapped_column(Integer, nullable=True)
    salt: MappedColumn[bytes] = mapped_column(LargeBinary, nullable=True)
    encrypted_secret: MappedColumn[bytes] = mapped_column(LargeBinary, nullable=True)
    
    user: Mapped["User"] = relationship("User", back_populates="secrets")
    
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_user_name"),
    )
    
    def set_secret(self, secret: bytes):
        self.encrypted_secret = security.fernet.encrypt(secret)
        
    def get_secret(self) -> bytes:
        return security.fernet.decrypt(self.encrypted_secret)
    
    @classmethod
    def create_secrets(cls, user_id: int):
        """Creates the empty required secrets.
        Must be called after db.session.flush() when creating a user.
        
        Args:
            user_id (int): The ID of the user who owns the secrets
        """
        stored_key_secret = Secret(user_id=user_id, name="SCRAM Stored Key")
        server_key_secret = Secret(user_id=user_id, name="SCRAM Server Key")
        vault_key_secret = Secret(user_id=user_id, name="Vault Key")
        totp_secret = Secret(user_id=user_id, name="TOTP")
        db.session.add_all([stored_key_secret, server_key_secret, vault_key_secret, totp_secret])