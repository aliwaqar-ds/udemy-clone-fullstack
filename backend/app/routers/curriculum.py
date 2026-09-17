from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
import app.models as models
import app.schemas as schemas
from app.routers.auth import get_current_user
from app.routers.courses import require_instructor

router = APIRouter(prefix="/api/v1", tags=["Curriculum & Learning"])


# --- Section Endpoints ---

@router.post(
    "/sections",
    response_model=schemas.SectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_section(
    section_in: schemas.SectionCreate,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == section_in.course_id)
        .first()
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
        )

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add sections to your own courses.",
        )

    new_section = models.Section(**section_in.model_dump())
    db.add(new_section)
    db.commit()
    db.refresh(new_section)
    return new_section


@router.delete("/sections/{section_id}", status_code=status.HTTP_200_OK)
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

@router.post(
    "/lessons",
    response_model=schemas.LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lesson(
    lesson_in: schemas.LessonCreate,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
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
    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add lessons to your own sections.",
        )

    new_lesson = models.Lesson(**lesson_in.model_dump())
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_200_OK)
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


@router.get(
    "/courses/{course_id}/curriculum",
    response_model=list[schemas.SectionResponse],
)
def get_course_curriculum(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
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

@router.post(
    "/enrollments",
    response_model=schemas.EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def enroll_in_course(
    enrollment_in: schemas.EnrollmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = (
        db.query(models.Course)
        .filter(models.Course.id == enrollment_in.course_id)
        .first()
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found."
        )

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


@router.get(
    "/enrollments/me",
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

    return db.query(models.Course).filter(models.Course.id.in_(course_ids)).all()


@router.post(
    "/lessons/{lesson_id}/toggle-complete",
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
        return {"lesson_id": lesson_id, "is_completed": progress.is_completed}

    new_progress = models.LessonProgress(
        user_id=current_user.id, lesson_id=lesson_id, is_completed=True
    )
    db.add(new_progress)
    db.commit()
    return {"lesson_id": lesson_id, "is_completed": True}


@router.get(
    "/courses/{course_id}/progress",
    response_model=schemas.CourseProgressResponse,
)
def get_course_progress(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sections = db.query(models.Section).filter(models.Section.course_id == course_id).all()
    section_ids = [s.id for s in sections]

    lessons = db.query(models.Lesson).filter(models.Lesson.section_id.in_(section_ids)).all()
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