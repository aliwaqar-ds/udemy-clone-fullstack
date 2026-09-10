from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Signup Request Schema
class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    role: Optional[str] = "student"  # 'student' or 'instructor'


# Public User Response Schema (Excludes password hash & OTP)
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone_number: str
    role: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


# OTP Verification Request Schema
class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)

# Login Request Schema
class UserLogin(BaseModel):
  email: EmailStr
  password: str


# Token Response Schema
class Token(BaseModel):
  access_token: str
  token_type: str = "bearer"


class TokenData(BaseModel):
  email: Optional[str] = None
  role: Optional[str] = None
  