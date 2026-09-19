from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False)  # 'student', 'instructor', 'admin'
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String(6), nullable=True)
    otp_created_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    courses = relationship("Course", back_populates="instructor")
    transactions = relationship("Transaction", back_populates="user")
    payouts = relationship("Payout", back_populates="instructor")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    courses = relationship("Course", back_populates="category")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), default=0.00, nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor = relationship("User", back_populates="courses")
    category = relationship("Category", back_populates="courses")
    sections = relationship("Section", back_populates="course", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="course")


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    order = Column(Integer, default=1, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Relationships
    course = relationship("Course", back_populates="sections")
    lessons = relationship(
        "Lesson", back_populates="section", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    video_url = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=0)
    order = Column(Integer, default=1, nullable=False)
    is_free_preview = Column(Boolean, default=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    # Relationships
    section = relationship("Section", back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="enrollments")
    course = relationship("Course", backref="enrollments")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    is_completed = Column(Boolean, default=True)
    completed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="progress_records")
    lesson = relationship("Lesson", backref="progress_records")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User")
    course = relationship("Course")


# --- Financial & Payment Simulator Models ---

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    instructor_earnings = Column(Numeric(10, 2), nullable=False)  # 80% share
    platform_fee = Column(Numeric(10, 2), nullable=False)         # 20% share
    payment_method = Column(String(50), default="Card (Simulator)")
    status = Column(String(20), default="completed")              # completed, refunded
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    user = relationship("User", back_populates="transactions")
    course = relationship("Course", back_populates="transactions")


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payout_method = Column(String(100), nullable=False)          # e.g., "PayPal: instructor@email.com"
    status = Column(String(20), default="processed")              # pending, processed
    requested_at = Column(DateTime, default=datetime.utcnow)

    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    instructor = relationship("User", back_populates="payouts")