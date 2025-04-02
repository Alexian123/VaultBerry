from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from typing import TYPE_CHECKING
from app import db

if TYPE_CHECKING:
    from .user import User

class KeyChain(db.Model):
    __tablename__ = "keychains"
    
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    salt: MappedColumn[str] = mapped_column(String(24))   # Base64 encoded
    vault_key: MappedColumn[str] = mapped_column(String(255)) # Encrypted and Base64 encoded
    recovery_key: MappedColumn[str] = mapped_column(String(255))  # Encrypted and Base64 encoded
    
    user: Mapped["User"] = relationship("User", back_populates="keychain")

    def to_dict(self):
        return {
            "salt": self.salt,
            "vault_key": self.vault_key,
            "recovery_key": self.recovery_key
        }