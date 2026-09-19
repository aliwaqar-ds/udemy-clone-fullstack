# backend/seed_data.py
from app.database import SessionLocal
from app.models import User, Course, Section, Lesson
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    try:
        print("🌱 Seeding realistic LMS data...")

        hashed_password = pwd_context.hash("Password123!")

        # 1. Create Professional Instructors
        instructor_1 = User(
            full_name="Dr. Angela Yu",
            email="angela.yu@appbrewery.com",
            phone_number="+14155552671",
            password_hash=hashed_password,
            role="instructor",
            is_verified=True
        )
        instructor_2 = User(
            full_name="Maximilian Schwarzmüller",
            email="max@academind.com",
            phone_number="+491515552672",
            password_hash=hashed_password,
            role="instructor",
            is_verified=True
        )

        # 2. Create Realistic Students
        student_1 = User(
            full_name="Alex Morgan",
            email="alex.morgan@gmail.com",
            phone_number="+12125550198",
            password_hash=hashed_password,
            role="student",
            is_verified=True
        )

        db.add_all([instructor_1, instructor_2, student_1])
        db.commit()
        db.refresh(instructor_1)
        db.refresh(instructor_2)

        # 3. Create Udemy-Style Courses
        courses_data = [
            {
                "instructor_id": instructor_1.id,
                "title": "The Complete 2026 Web Development Bootcamp",
                "category": "Web Development",
                "description": "Become a Full-Stack Developer with HTML5, CSS3, JavaScript ES6, React 19, FastAPI, and PostgreSQL.",
                "price": 84.99,
                "thumbnail_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800",
                "is_published": True,
                "sections": [
                    {"title": "Section 1: Frontend Foundations", "lessons": ["HTML Syntax & Structure", "CSS Layouts & Flexbox"]},
                    {"title": "Section 2: Modern JavaScript & React", "lessons": ["ES6 Array Methods", "React State & Hooks"]}
                ]
            },
            {
                "instructor_id": instructor_2.id,
                "title": "Python for Data Science & Machine Learning Masterclass",
                "category": "Data Science & ML",
                "description": "Learn NumPy, Pandas, Matplotlib, Scikit-Learn, and Deep Learning with PyTorch step-by-step.",
                "price": 94.99,
                "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
                "is_published": True,
                "sections": [
                    {"title": "Section 1: Python Essentials", "lessons": ["Data Types & Logic Loops", "Functions & Lambdas"]},
                    {"title": "Section 2: Data Analysis", "lessons": ["Pandas DataFrames", "Data Visualization"]}
                ]
            },
            {
                "instructor_id": instructor_1.id,
                "title": "React Native & Expo: Build iOS & Android Mobile Apps",
                "category": "Mobile Development",
                "description": "Master cross-platform mobile development with React Native, Navigation, Native APIs, and Cloud Sync.",
                "price": 69.99,
                "thumbnail_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800",
                "is_published": True,
                "sections": [
                    {"title": "Section 1: Getting Started with Expo", "lessons": ["Expo CLI Setup", "JSX Components"]},
                ]
            }
        ]

        for c in courses_data:
            course = Course(
                instructor_id=c["instructor_id"],
                title=c["title"],
                category=c["category"],
                description=c["description"],
                price=c["price"],
                thumbnail_url=c["thumbnail_url"],
                is_published=c["is_published"]
            )
            db.add(course)
            db.commit()
            db.refresh(course)

            for s_idx, sec in enumerate(c["sections"]):
                section = Section(course_id=course.id, title=sec["title"], order_index=s_idx)
                db.add(section)
                db.commit()
                db.refresh(section)

                for l_idx, l_title in enumerate(sec["lessons"]):
                    lesson = Lesson(
                        course_id=course.id,
                        section_title=sec["title"],
                        title=l_title,
                        lesson_type="video",
                        duration_minutes=12,
                        order_index=l_idx
                    )
                    db.add(lesson)
            db.commit()

        print("✨ Seeding complete! All dummy data is ready for demo recording.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()