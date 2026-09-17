from datetime import datetime, timedelta
from fastapi.staticfiles import StaticFiles
import os
import sys

# Ensure backend directory is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

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

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed default categories if missing
    db: Session = next(get_db())
    categories_data = [
        {"id": 1, "name": "Web Development", "slug": "web-development"},
        {"id": 2, "name": "Data Science & ML", "slug": "data-science-ml"},
        {"id": 3, "name": "Mobile Development", "slug": "mobile-development"},
        {"id": 4, "name": "Programming Languages", "slug": "programming-languages"},
        {"id": 5, "name": "Database & SQL", "slug": "database-sql"},
        {"id": 6, "name": "Design & UI/UX", "slug": "design-ui-ux"},
    ]
    for cat in categories_data:
        existing_cat = db.query(models.Category).filter(models.Category.id == cat["id"]).first()
        if not existing_cat:
            db.add(models.Category(**cat))
    db.commit()
    db.close()
    yield

# Update your FastAPI instantiation line to pass lifespan:
app = FastAPI(title="Udemy Clone API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Ensure uploads directory exists
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)

# Mount static directory for serving uploads
app.mount("/static", StaticFiles(directory="uploads"), name="static")
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

@app.get(
    "/api/v1/instructor/courses",
    response_model=list[schemas.CourseResponse],
)
def list_instructor_courses(
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    """Fetch all courses created by the currently logged-in instructor."""
    return (
        db.query(models.Course)
        .filter(models.Course.instructor_id == current_user.id)
        .all()
    )

@app.get(
    "/api/v1/courses/{course_id}",
    response_model=schemas.CourseResponse,
)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == course_id, models.Course.is_published == True)
        .first()
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found.",
        )
    return course

@app.patch(
    "/api/v1/courses/{course_id}/publish",
    response_model=schemas.CourseResponse,
)
def toggle_publish_course(
    course_id: int,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == course_id)
        .first()
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
        )

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only publish your own courses.",
        )

    course.is_published = not course.is_published
    db.commit()
    db.refresh(course)
    return course

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

# --- Delete Section Route ---
@app.delete(
    "/api/v1/sections/{section_id}",
    status_code=status.HTTP_200_OK,
)
def delete_section(
    section_id: int,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Section not found."
        )

    course = db.query(models.Course).filter(models.Course.id == section.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete sections from your own courses.",
        )

    db.delete(section)
    db.commit()
    return {"message": "Section deleted successfully"}


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


# --- Delete Lesson Route ---
@app.delete(
    "/api/v1/lessons/{lesson_id}",
    status_code=status.HTTP_200_OK,
)
def delete_lesson(
    lesson_id: int,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found."
        )

    section = db.query(models.Section).filter(models.Section.id == lesson.section_id).first()
    course = db.query(models.Course).filter(models.Course.id == section.course_id).first()
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete lessons from your own courses.",
        )

    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}


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

# --- Enrollment & Progress Endpoints ---


@app.post(
    "/api/v1/enrollments",
    response_model=schemas.EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def enroll_in_course(
    enrollment_in: schemas.EnrollmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
  # Check if course exists
  course = (
      db.query(models.Course)
      .filter(models.Course.id == enrollment_in.course_id)
      .first()
  )
  if not course:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
    )

  # Check if already enrolled
  existing_enrollment = (
      db.query(models.Enrollment)
      .filter(
          models.Enrollment.user_id == current_user.id,
          models.Enrollment.course_id == enrollment_in.course_id,
      )
      .first()
  )
  if existing_enrollment:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Already enrolled in this course.",
    )

  new_enrollment = models.Enrollment(
      user_id=current_user.id, course_id=enrollment_in.course_id
  )
  db.add(new_enrollment)
  db.commit()
  db.refresh(new_enrollment)
  return new_enrollment

@app.get(
    "/api/v1/enrollments/me",
    response_model=list[schemas.CourseResponse],
)
def get_my_enrolled_courses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enrollments = (
        db.query(models.Enrollment)
        .filter(models.Enrollment.user_id == current_user.id)
        .all()
    )
    course_ids = [e.course_id for e in enrollments]
    if not course_ids:
        return []
    
    courses = (
        db.query(models.Course)
        .filter(models.Course.id.in_(course_ids))
        .all()
    )
    return courses

@app.post(
    "/api/v1/lessons/{lesson_id}/toggle-complete",
    response_model=schemas.ProgressToggleResponse,
)
def toggle_lesson_completion(
    lesson_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
  lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
  if not lesson:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found."
    )

  progress = (
      db.query(models.LessonProgress)
      .filter(
          models.LessonProgress.user_id == current_user.id,
          models.LessonProgress.lesson_id == lesson_id,
      )
      .first()
  )

  if progress:
    progress.is_completed = not progress.is_completed
    db.commit()
    db.refresh(progress)
    return {
        "lesson_id": lesson_id,
        "is_completed": progress.is_completed,
    }

  new_progress = models.LessonProgress(
      user_id=current_user.id, lesson_id=lesson_id, is_completed=True
  )
  db.add(new_progress)
  db.commit()
  return {"lesson_id": lesson_id, "is_completed": True}


@app.get(
    "/api/v1/courses/{course_id}/progress",
    response_model=schemas.CourseProgressResponse,
)
def get_course_progress(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
  # Get all lesson IDs for this course across all sections
  sections = (
      db.query(models.Section)
      .filter(models.Section.course_id == course_id)
      .all()
  )
  section_ids = [s.id for s in sections]

  lessons = (
      db.query(models.Lesson)
      .filter(models.Lesson.section_id.in_(section_ids))
      .all()
  )
  total_lessons = len(lessons)

  if total_lessons == 0:
    return {
        "course_id": course_id,
        "total_lessons": 0,
        "completed_lessons": 0,
        "progress_percentage": 0.0,
    }

  lesson_ids = [l.id for l in lessons]
  completed_count = (
      db.query(models.LessonProgress)
      .filter(
          models.LessonProgress.user_id == current_user.id,
          models.LessonProgress.lesson_id.in_(lesson_ids),
          models.LessonProgress.is_completed == True,
      )
      .count()
  )

  percentage = round((completed_count / total_lessons) * 100, 2)
  return {
      "course_id": course_id,
      "total_lessons": total_lessons,
      "completed_lessons": completed_count,
      "progress_percentage": percentage,
  }

import uuid
from fastapi import File, UploadFile

# Allowed file extensions
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/mkv", "video/webm"]


@app.post("/api/v1/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_instructor),
):
  if file.content_type not in ALLOWED_IMAGE_TYPES:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            "Invalid image format. Allowed formats: JPEG, PNG, WebP."
        ),
    )

  file_extension = os.path.splitext(file.filename)[1]
  unique_filename = f"{uuid.uuid4()}{file_extension}"
  file_path = os.path.join("uploads/images", unique_filename)

  with open(file_path, "wb") as buffer:
    buffer.write(await file.read())

  return {
      "filename": unique_filename,
      "url": f"http://127.0.0.1:8000/static/images/{unique_filename}",
  }


@app.post("/api/v1/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_instructor),
):
  if file.content_type not in ALLOWED_VIDEO_TYPES:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid video format. Allowed formats: MP4, MKV, WebM.",
    )

  file_extension = os.path.splitext(file.filename)[1]
  unique_filename = f"{uuid.uuid4()}{file_extension}"
  file_path = os.path.join("uploads/videos", unique_filename)

  with open(file_path, "wb") as buffer:
    buffer.write(await file.read())

  return {
      "filename": unique_filename,
      "url": f"http://127.0.0.1:8000/static/videos/{unique_filename}",
  }

import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")


@app.post("/api/v1/payments/create-checkout-session/{course_id}")
def create_checkout_session(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
        )

    # Check if already enrolled
    existing_enrollment = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.user_id == current_user.id,
            models.Enrollment.course_id == course_id,
        )
        .first()
    )
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this course.",
        )

    # Auto-enroll student directly for testing (bypassing real Stripe redirect)
    new_enrollment = models.Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(new_enrollment)
    db.commit()

    # Return frontend success page URL directly
    return {"checkout_url": "http://localhost:5173/payment-success?session_id=mock_session_123"}

# --- Review Endpoints ---

@app.post("/api/v1/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify user enrollment
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.course_id == review_in.course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review courses you are enrolled in."
        )

    # Check for existing review
    existing_review = db.query(models.Review).filter(
        models.Review.user_id == current_user.id,
        models.Review.course_id == review_in.course_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this course."
        )

    new_review = models.Review(
        user_id=current_user.id,
        course_id=review_in.course_id,
        rating=review_in.rating,
        comment=review_in.comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@app.get("/api/v1/courses/{course_id}/reviews", response_model=list[schemas.ReviewResponse])
def get_course_reviews(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.course_id == course_id).all()