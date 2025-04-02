from sqlalchemy import Integer, String, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from typing import TYPE_CHECKING
from app import db

if TYPE_CHECKING:
    from .user import User

class OneTimePassword(db.Model):
    __tablename__ = "otps"
    
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    otp: MappedColumn[str] = mapped_column(String(9))
    created_at: MappedColumn[int] = mapped_column(BigInteger)
    expires_at: MappedColumn[int] = mapped_column(BigInteger)
    used: MappedColumn[bool] = mapped_column(Boolean, default=False)
    
    user: Mapped["User"] = relationship("User", back_populates="otps")