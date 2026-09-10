from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False) # 'student', 'instructor', 'admin'
    is_verified = Column(Boolean, default=False) # Email OTP status
    otp_code = Column(String(6), nullable=True) # OTP storage
    otp_created_at = Column(DateTime, nullable=True) # OTP expiration check
    created_at = Column(DateTime, default=datetime.utcnow)