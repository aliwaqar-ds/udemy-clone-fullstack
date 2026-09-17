import os
import uuid
import stripe
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
import app.models as models
import app.schemas as schemas
from app.routers.auth import get_current_user
from app.routers.courses import require_instructor

router = APIRouter(prefix="/api/v1", tags=["Services & Reviews"])

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/mkv", "video/webm"]

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")


# --- Upload Endpoints ---

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_instructor),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed formats: JPEG, PNG, WebP.",
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


@router.post("/upload/video")
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


# --- Payment Endpoints ---

@router.post("/payments/create-checkout-session/{course_id}")
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

    new_enrollment = models.Enrollment(user_id=current_user.id, course_id=course_id)
    db.add(new_enrollment)
    db.commit()

    return {"checkout_url": "http://localhost:5173/payment-success?session_id=mock_session_123"}


# --- Review Endpoints ---

@router.post("/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current_user.id,
        models.Enrollment.course_id == review_in.course_id
    ).first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review courses you are enrolled in."
        )

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


@router.get("/courses/{course_id}/reviews", response_model=list[schemas.ReviewResponse])
def get_course_reviews(course_id: int, db: Session = Depends(get_db)):
    return db.query(models.Review).filter(models.Review.course_id == course_id).all()