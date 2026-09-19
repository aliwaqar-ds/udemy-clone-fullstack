from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
import app.models as models
import app.schemas as schemas
from app.routers.auth import get_current_user
from app.routers.courses import require_instructor

router = APIRouter(prefix="/api/v1/financials", tags=["Payments & Payouts"])


# --- Student Checkout (Dummy Payment Simulator) ---

@router.post("/checkout", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def process_checkout(
    checkout_in: schemas.CheckoutRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Verify course exists
    course = db.query(models.Course).filter(models.Course.id == checkout_in.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found."
        )

    # 2. Prevent duplicate enrollment
    existing_enrollment = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.user_id == current_user.id,
            models.Enrollment.course_id == checkout_in.course_id,
        )
        .first()
    )
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this course."
        )

    # 3. Calculate 80/20 platform split
    total_price = float(course.price)
    instructor_share = round(total_price * 0.80, 2)
    platform_fee = round(total_price * 0.20, 2)

    # 4. Record transaction in database
    new_transaction = models.Transaction(
        amount=total_price,
        instructor_earnings=instructor_share,
        platform_fee=platform_fee,
        payment_method="Card (Simulator)",
        status="completed",
        user_id=current_user.id,
        course_id=course.id,
    )
    db.add(new_transaction)

    # 5. Automatically enroll student in course
    new_enrollment = models.Enrollment(
        user_id=current_user.id,
        course_id=course.id,
    )
    db.add(new_enrollment)

    db.commit()
    db.refresh(new_transaction)
    return new_transaction


# --- Instructor Financial Overview & Earnings ---

@router.get("/instructor/overview", response_model=schemas.InstructorFinancialsResponse)
def get_instructor_financial_overview(
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    # Get instructor's courses
    instructor_courses = (
        db.query(models.Course)
        .filter(models.Course.instructor_id == current_user.id)
        .all()
    )
    course_ids = [c.id for c in instructor_courses]

    if not course_ids:
        return {
            "gross_revenue": 0.0,
            "instructor_earnings": 0.0,
            "total_withdrawn": 0.0,
            "available_balance": 0.0,
            "transactions": [],
            "payouts": [],
        }

    # Fetch all completed transactions for instructor's courses
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.course_id.in_(course_ids))
        .order_by(models.Transaction.created_at.desc())
        .all()
    )

    gross_revenue = sum(float(t.amount) for t in transactions)
    instructor_earnings = sum(float(t.instructor_earnings) for t in transactions)

    # Fetch all payout requests for this instructor
    payouts = (
        db.query(models.Payout)
        .filter(models.Payout.instructor_id == current_user.id)
        .order_by(models.Payout.requested_at.desc())
        .all()
    )

    total_withdrawn = sum(float(p.amount) for p in payouts if p.status == "processed")
    available_balance = round(instructor_earnings - total_withdrawn, 2)

    return {
        "gross_revenue": round(gross_revenue, 2),
        "instructor_earnings": round(instructor_earnings, 2),
        "total_withdrawn": round(total_withdrawn, 2),
        "available_balance": max(0.0, available_balance),
        "transactions": transactions,
        "payouts": payouts,
    }


# --- Instructor Payout Request Simulator ---

@router.post("/instructor/request-payout", response_model=schemas.PayoutResponse, status_code=status.HTTP_201_CREATED)
def request_instructor_payout(
    payout_in: schemas.PayoutRequest,
    current_user: models.User = Depends(require_instructor),
    db: Session = Depends(get_db),
):
    # Fetch instructor's courses and financial records
    instructor_courses = (
        db.query(models.Course)
        .filter(models.Course.instructor_id == current_user.id)
        .all()
    )
    course_ids = [c.id for c in instructor_courses]

    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.course_id.in_(course_ids))
        .all()
    )
    total_earnings = sum(float(t.instructor_earnings) for t in transactions)

    payouts = (
        db.query(models.Payout)
        .filter(models.Payout.instructor_id == current_user.id)
        .all()
    )
    total_withdrawn = sum(float(p.amount) for p in payouts if p.status == "processed")
    available_balance = round(total_earnings - total_withdrawn, 2)

    # Validate withdrawal amount
    if payout_in.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Your available withdrawable balance is ${available_balance:.2f}."
        )

    # Create payout record
    new_payout = models.Payout(
        amount=payout_in.amount,
        payout_method=payout_in.payout_method,
        status="processed",
        instructor_id=current_user.id,
    )
    db.add(new_payout)
    db.commit()
    db.refresh(new_payout)

    return new_payout