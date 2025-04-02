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