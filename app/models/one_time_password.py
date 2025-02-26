from sqlalchemy import Integer, VARCHAR, BigInteger, Boolean
from sqlalchemy.orm import mapped_column
from app import db

class OneTimePassword(db.Model):
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, db.ForeignKey('user.id'))
    otp = mapped_column(VARCHAR(9), unique=True)
    created_at = mapped_column(BigInteger)
    expires_at = mapped_column(BigInteger)
    used = mapped_column(Boolean, default=False)

    def to_dict_full(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'otp': self.otp,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'used': self.used
        }