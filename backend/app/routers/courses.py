from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
import app.models as models
import app.schemas as schemas
from app.routers.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["Courses & Categories"])


# RBAC Dependency: Require Instructor or Admin Role
def require_instructor(current_user: models.User = Depends(get_current_user)):
    if current_user.role not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Only instructors or admins can perform this action.",
        )
    return current_user


# --- Category Endpoints ---

@router.post(
    "/categories",
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


@router.get("/categories", response_model=list[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


# --- Course Endpoints ---

@router.post(
    "/courses",
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


@router.get("/courses", response_model=list[schemas.CourseResponse])
def list_published_courses(
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Course).filter(models.Course.is_published == True)

    if search:
        query = query.filter(models.Course.title.ilike(f"%{search}%"))

    if category_id:
        query = query.filter(models.Course.category_id == category_id)

    return query.all()


@router.get(
    "/instructor/courses",
    response_model=list[schemas.CourseResponse],
)
def list_instructor_courses(
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Course)
        .filter(models.Course.instructor_id == current_user.id)
        .all()
    )


@router.get(
    "/courses/{course_id}",
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


@router.patch(
    "/courses/{course_id}/publish",
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