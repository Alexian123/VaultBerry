from sqlalchemy import Integer, VARCHAR, BigInteger, Boolean
from sqlalchemy.orm import mapped_column
from app import db

class OneTimePassword(db.Model):
    __tablename__ = 'one_time_password'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, db.ForeignKey('users.id'))
    otp = mapped_column(VARCHAR(9))
    created_at = mapped_column(BigInteger)
    expires_at = mapped_column(BigInteger)
    used = mapped_column(Boolean, default=False)