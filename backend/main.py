from datetime import datetime, timedelta
import os
import sys

# Ensure backend directory is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
import app.models as models
import app.schemas as schemas
from app.utils import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    generate_otp,
    hash_password,
    verify_password,
)

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Udemy Clone API")
security = HTTPBearer()


# Get current authenticated user dependency
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# RBAC: Require Instructor or Admin Role
def require_instructor(current_user: models.User = Depends(get_current_user)):
  if current_user.role not in ["instructor", "admin"]:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "Access forbidden. Only instructors or admins can perform this"
            " action."
        ),
    )
  return current_user


@app.get("/")
def read_root():
    return {"message": "Udemy Clone Backend is running!"}


# 1. User Registration Route
@app.post(
    "/api/v1/auth/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User).filter(models.User.email == user_in.email).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered.",
        )

    otp = generate_otp()
    hashed_pwd = hash_password(user_in.password)

    new_user = models.User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        password_hash=hashed_pwd,
        role=user_in.role or "student",
        is_verified=False,
        otp_code=otp,
        otp_created_at=datetime.utcnow(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"\n[OTP EMAIL SIMULATION] Code for {new_user.email}: {otp}\n")
    return new_user


# 2. OTP Verification Route
@app.post("/api/v1/auth/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(payload: schemas.OTPVerify, db: Session = Depends(get_db)):
    user = (
        db.query(models.User).filter(models.User.email == payload.email).first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )

    if user.is_verified:
        return {"message": "Account is already verified."}

    if user.otp_code != payload.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code."
        )

    if user.otp_created_at and datetime.utcnow() - user.otp_created_at > timedelta(
        minutes=10
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired. Please request a new one.",
        )

    user.is_verified = True
    user.otp_code = None
    db.commit()

    return {"message": "Email verified successfully! Account is now active."}


# 3. User Login Route
@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(models.User).filter(models.User.email == payload.email).first()
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify your email first.",
        )

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 4. Get Active User Profile (Protected Route)
@app.get("/api/v1/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# --- Category Endpoints ---


@app.post(
    "/api/v1/categories",
    response_model=schemas.CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_in: schemas.CategoryCreate,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
  existing_cat = (
      db.query(models.Category)
      .filter(
          (models.Category.name == category_in.name)
          | (models.Category.slug == category_in.slug)
      )
      .first()
  )
  if existing_cat:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Category name or slug already exists.",
    )

  new_cat = models.Category(**category_in.model_dump())
  db.add(new_cat)
  db.commit()
  db.refresh(new_cat)
  return new_cat


@app.get("/api/v1/categories", response_model=list[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
  return db.query(models.Category).all()


# --- Course Endpoints ---


@app.post(
    "/api/v1/courses",
    response_model=schemas.CourseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_course(
    course_in: schemas.CourseCreate,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
  existing_course = (
      db.query(models.Course)
      .filter(models.Course.slug == course_in.slug)
      .first()
  )
  if existing_course:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Course slug already exists.",
    )

  new_course = models.Course(
      **course_in.model_dump(), instructor_id=current_user.id
  )
  db.add(new_course)
  db.commit()
  db.refresh(new_course)
  return new_course


@app.get("/api/v1/courses", response_model=list[schemas.CourseResponse])
def list_published_courses(db: Session = Depends(get_db)):
  return (
      db.query(models.Course).filter(models.Course.is_published == True).all()
  )

# --- Section Endpoints ---


@app.post(
    "/api/v1/sections",
    response_model=schemas.SectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_section(
    section_in: schemas.SectionCreate,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
  # Check if course exists and belongs to instructor
  course = (
      db.query(models.Course)
      .filter(models.Course.id == section_in.course_id)
      .first()
  )
  if not course:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
    )

  if (
      course.instructor_id != current_user.id
      and current_user.role != "admin"
  ):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You can only add sections to your own courses.",
    )

  new_section = models.Section(**section_in.model_dump())
  db.add(new_section)
  db.commit()
  db.refresh(new_section)
  return new_section


# --- Lesson Endpoints ---


@app.post(
    "/api/v1/lessons",
    response_model=schemas.LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    lesson_in: schemas.LessonCreate,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
  # Verify section and course ownership
  section = (
      db.query(models.Section)
      .filter(models.Section.id == lesson_in.section_id)
      .first()
  )
  if not section:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Section not found."
    )

  course = (
      db.query(models.Course)
      .filter(models.Course.id == section.course_id)
      .first()
  )
  if (
      course.instructor_id != current_user.id
      and current_user.role != "admin"
  ):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You can only add lessons to your own sections.",
    )

  new_lesson = models.Lesson(**lesson_in.model_dump())
  db.add(new_lesson)
  db.commit()
  db.refresh(new_lesson)
  return new_lesson


# --- Get Full Course Curriculum Route ---


@app.get(
    "/api/v1/courses/{course_id}/curriculum",
    response_model=list[schemas.SectionResponse],
)
def get_course_curriculum(course_id: int, db: Session = Depends(get_db)):
  course = (
      db.query(models.Course).filter(models.Course.id == course_id).first()
  )
  if not course:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
    )

  sections = (
      db.query(models.Section)
      .filter(models.Section.course_id == course_id)
      .order_by(models.Section.order.asc())
      .all()
  )
  return sections