from sqlalchemy import Integer, String, Text, ForeignKey, UniqueConstraint, BigInteger, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from base64 import b64encode, b64decode
from typing import TYPE_CHECKING
from app import db

if TYPE_CHECKING:
    from .user import User

class VaultEntry(db.Model):
    
    __tablename__ = "entries"
    
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    last_modified: MappedColumn[int] = mapped_column(BigInteger)
    title: MappedColumn[str] = mapped_column(String(255))
    url: MappedColumn[str] = mapped_column(String(255), nullable=True)    # Plaintext
    encrypted_username: MappedColumn[bytes] = mapped_column(LargeBinary, nullable=True)
    encrypted_password: MappedColumn[bytes] = mapped_column(LargeBinary, nullable=True)
    notes: MappedColumn[str] = mapped_column(Text, nullable=True)  # Plaintext

    user: Mapped["User"] = relationship("User", back_populates="entries")

    __table_args__ = (
        # An individual user can't have multiple entries with the same title
        UniqueConstraint("user_id", "title", name="_user_title_uc"),
    )

    # Dictionary containing the full entry
    def to_detailed_dict(self):
        encrypted_username = b64encode(self.encrypted_username).decode() if self.encrypted_username else None
        encrypted_password = b64encode(self.encrypted_password).decode() if self.encrypted_password else None
        return {
            "title": self.title,
            "url": self.url,
            "encrypted_username": encrypted_username,
            "encrypted_password": encrypted_password,
            "notes": self.notes
        }
        
    # Dictionary containing the entry preview
    def to_preview_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }
        
    def set_encrypted_fields(self, username: str | None, password: str | None):
        """Decodes and sets the encrypted fields.
        
        Args:
            username (str): The base64 encoded encrypted username
            password (str): The base64 encoded encrypted password
        """
        if username is not None:
            self.encrypted_username = b64decode(username)
        if password is not None:
            self.encrypted_password = b64decode(password)