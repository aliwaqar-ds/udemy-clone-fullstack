# backend/app/seed_data.py
import bcrypt
import re
from app.database import SessionLocal
from app.models import User, Course, Section, Lesson

def get_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[\s_-]+', '-', text)

def seed():
    db = SessionLocal()
    try:
        print("🌱 Seeding realistic LMS data...")

        hashed_password = get_hash("Pass123!")

        # Helper function to get or create users safely
        def get_or_create_user(full_name, email, phone_number, role):
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return existing
            user = User(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                password_hash=hashed_password,
                role=role,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        # 1. Create Instructors & Student
        instructor_1 = get_or_create_user("Dr. Angela Yu", "angela.yu@appbrewery.com", "+14155552671", "instructor")
        instructor_2 = get_or_create_user("Maximilian Schwarzmüller", "max@academind.com", "+491515552672", "instructor")
        student_1 = get_or_create_user("Alex Morgan", "alex.morgan@gmail.com", "+12125550198", "student")

        # 2. Check if courses already exist
        if db.query(Course).first():
            print("✨ Database already contains course data!")
            return

        # 3. Create Courses Data
        courses_data = [
            {
                "instructor_id": instructor_1.id,
                "title": "The Complete 2026 Web Development Bootcamp",
                "description": "Become a Full-Stack Developer with HTML5, CSS3, JavaScript ES6, React, FastAPI, and PostgreSQL.",
                "price": 84.99,
                "thumbnail_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800",
                "sections": [
                    {"title": "Section 1: Frontend Foundations", "lessons": ["HTML Syntax & Structure", "CSS Layouts & Flexbox"]},
                    {"title": "Section 2: Modern JavaScript & React", "lessons": ["ES6 Array Methods", "React State & Hooks"]}
                ]
            },
            {
                "instructor_id": instructor_2.id,
                "title": "Python for Data Science & Machine Learning Masterclass",
                "description": "Learn NumPy, Pandas, Matplotlib, Scikit-Learn, and Deep Learning with PyTorch step-by-step.",
                "price": 94.99,
                "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
                "sections": [
                    {"title": "Section 1: Python Essentials", "lessons": ["Data Types & Logic Loops", "Functions & Lambdas"]},
                    {"title": "Section 2: Data Analysis", "lessons": ["Pandas DataFrames", "Data Visualization"]}
                ]
            },
            {
                "instructor_id": instructor_1.id,
                "title": "React Native & Expo: Build iOS & Android Mobile Apps",
                "description": "Master cross-platform mobile development with React Native, Navigation, Native APIs, and Cloud Sync.",
                "price": 69.99,
                "thumbnail_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800",
                "sections": [
                    {"title": "Section 1: Getting Started with Expo", "lessons": ["Expo CLI Setup", "JSX Components"]}
                ]
            }
        ]

        for item in courses_data:
            course = Course(
                instructor_id=item["instructor_id"],
                title=item["title"],
                slug=slugify(item["title"]),
                description=item["description"],
                price=item["price"],
                thumbnail_url=item["thumbnail_url"],
                is_published=True
            )
            db.add(course)
            db.commit()
            db.refresh(course)

            for s_idx, sec in enumerate(item["sections"]):
                section = Section(
                    course_id=course.id,
                    title=sec["title"],
                    order=s_idx + 1
                )
                db.add(section)
                db.commit()
                db.refresh(section)

                for l_idx, l_title in enumerate(sec["lessons"]):
                    lesson = Lesson(
                        section_id=section.id,  # Passed section_id instead of course_id
                        title=l_title,
                        duration_minutes=12,
                        order=l_idx + 1
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