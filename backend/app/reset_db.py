# backend/app/reset_db.py
from app.database import SessionLocal
import app.models as models

def reset_database():
    db = SessionLocal()
    try:
        print("🧹 Clearing database tables...")
        
        # Deletion order to safely handle foreign keys
        model_names = [
            'Transaction', 
            'Payout', 
            'Review', 
            'LessonProgress',
            'UserProgress', 
            'Progress', 
            'Enrollment', 
            'Lesson', 
            'Section', 
            'Course', 
            'User'
        ]
        
        for name in model_names:
            if hasattr(models, name):
                model_cls = getattr(models, name)
                db.query(model_cls).delete()
        
        db.commit()
        print("✅ Database successfully wiped!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error resetting database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()