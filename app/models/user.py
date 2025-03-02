from sqlalchemy import Integer, VARCHAR, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    
    __tablename__ = 'users'
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    keychain_id = mapped_column(Integer, ForeignKey('key_chain.id'), unique=True, nullable=True)
    email = mapped_column(VARCHAR(255), unique=True)
    hashed_password = mapped_column(VARCHAR(255))
    first_name = mapped_column(VARCHAR(255), nullable=True)
    last_name = mapped_column(VARCHAR(255), nullable=True)
    is_admin = mapped_column(Boolean, default=False)
    created_at = mapped_column(BigInteger)
    
    def account_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name
        }