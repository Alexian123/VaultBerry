from sqlalchemy import Integer, String, BigInteger, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, MappedColumn, relationship
from typing import TYPE_CHECKING
from app import db
from app.util import security, get_now_timestamp

 # TODO: Use for veification token
if TYPE_CHECKING:
    from .user import User

class OneTimePassword(db.Model):
    __tablename__ = "otps"
    
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(Enum("RECOVERY", "ACTIVATION", name="otp_type", native_enum=True))
    otp: MappedColumn[str] = mapped_column(String(255))
    created_at: MappedColumn[int] = mapped_column(BigInteger)
    expires_at: MappedColumn[int] = mapped_column(BigInteger)
    used: MappedColumn[bool] = mapped_column(Boolean, default=False)
    
    user: Mapped["User"] = relationship("User", back_populates="otps")
    
    def is_expired(self) -> bool:
        """
        Returns True if the OTP is expired, False otherwise.
        """
        return self.expires_at < get_now_timestamp()
    
    @classmethod
    def get_cooldown_remaining_seconds_for_user(self, user_id: int, type: str, cooldown_seconds: int = 86400) -> int:
        """Returns the remaining seconds if the cooldown is not expired, 0 otherwise.
        
        Args:
            user_id (int): The ID of the user.
            type (str): The type of OTP.
            cooldown_seconds (int): The number of seconds until the cooldown expires.
        """
        now = get_now_timestamp()
        last_otp: OneTimePassword = OneTimePassword.query.filter_by(user_id=user_id, type=type).order_by(OneTimePassword.created_at.desc()).first()
        ref_time = now - cooldown_seconds
        if last_otp and last_otp.created_at > ref_time:
            return last_otp.created_at - ref_time
        return 0
    
    @classmethod
    def create_recovery_otp(cls, user_id: int, expires_in_seconds: int = 300) -> str:
        """
        Creates a new recovery OTP for the given user.
        
        Args:
            user_id (int): The ID of the user.
            expires_in_seconds (int): The number of seconds until the OTP expires.
            
        Returns:
            str: The generated OTP.
        """
        now = get_now_timestamp()
        otp = security.generator.random_digits()
        expires_at = now + expires_in_seconds
        one_time_password = OneTimePassword(
            user_id=user_id,
            type="RECOVERY",
            otp=otp,
            created_at=now,
            expires_at=expires_at
        )
        db.session.add(one_time_password)
        return otp
    
    @classmethod
    def create_email_verification_otp(cls, user_id: int, expires_in_seconds: int = 86400) -> str:
        """
        Creates a new email verification OTP for the given user. 
        
        Args:
            user_id (int): The ID of the user.
            expires_in_seconds (int): The number of seconds until the OTP expires.
            
        Returns:
            str: The generated OTP.
        """
        now = get_now_timestamp()
        otp = security.generator.random_string(32)
        expires_at = now + expires_in_seconds
        one_time_password = OneTimePassword(
            user_id=user_id,
            type="ACTIVATION",
            otp=otp,
            created_at=now,
            expires_at=expires_at
        )
        db.session.add(one_time_password)
        return otp