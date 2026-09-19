# backend/reset_db.py
from app.database import SessionLocal, engine
from app.models import Transaction, Payout, Review, Progress, Enrollment, Lesson, Section, Course, User

def reset_database():
    db = SessionLocal()
    try:
        print("🧹 Clearing database tables...")
        db.query(Transaction).delete()
        db.query(Payout).delete()
        db.query(Review).delete()
        db.query(Progress).delete()
        db.query(Enrollment).delete()
        db.query(Lesson).delete()
        db.query(Section).delete()
        db.query(Course).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Database successfully wiped!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()