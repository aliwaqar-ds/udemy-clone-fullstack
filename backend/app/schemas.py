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

# --- Category Schemas ---
class CategoryBase(BaseModel):
  name: str = Field(..., min_length=2, max_length=100)
  slug: str = Field(..., min_length=2, max_length=100)


class CategoryCreate(CategoryBase):
  pass


class CategoryResponse(CategoryBase):
  id: int

  class Config:
    from_attributes = True


# --- Course Schemas ---
class CourseBase(BaseModel):
  title: str = Field(..., min_length=3, max_length=255)
  slug: str = Field(..., min_length=3, max_length=255)
  description: Optional[str] = None
  price: float = Field(default=0.0, ge=0.0)
  category_id: Optional[int] = None


class CourseCreate(CourseBase):
  is_published: Optional[bool] = False


class CourseResponse(CourseBase):
  id: int
  is_published: bool
  instructor_id: int
  created_at: datetime
  updated_at: datetime

  class Config:
    from_attributes = True

# --- Lesson Schemas ---
class LessonBase(BaseModel):
  title: str = Field(..., min_length=2, max_length=255)
  video_url: Optional[str] = None
  content: Optional[str] = None
  duration_minutes: int = Field(default=0, ge=0)
  order: int = Field(default=1, ge=1)
  is_free_preview: bool = False


class LessonCreate(LessonBase):
  section_id: int


class LessonResponse(LessonBase):
  id: int
  section_id: int

  class Config:
    from_attributes = True


# --- Section Schemas ---
class SectionBase(BaseModel):
  title: str = Field(..., min_length=2, max_length=255)
  order: int = Field(default=1, ge=1)


class SectionCreate(SectionBase):
  course_id: int


class SectionResponse(SectionBase):
  id: int
  course_id: int
  lessons: list[LessonResponse] = []

  class Config:
    from_attributes = True

# --- Enrollment Schemas ---
class EnrollmentCreate(BaseModel):
  course_id: int


class EnrollmentResponse(BaseModel):
  id: int
  user_id: int
  course_id: int
  enrolled_at: datetime

  class Config:
    from_attributes = True


# --- Progress Schemas ---
class ProgressToggleResponse(BaseModel):
  lesson_id: int
  is_completed: bool


class CourseProgressResponse(BaseModel):
  course_id: int
  total_lessons: int
  completed_lessons: int
  progress_percentage: float