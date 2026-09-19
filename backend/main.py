from contextlib import asynccontextmanager
import os
import sys

# Ensure backend directory is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
import app.models as models
from app.routers import auth, courses, curriculum, services, payments

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)


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
        existing_cat = (
            db.query(models.Category)
            .filter(models.Category.id == cat["id"])
            .first()
        )
        if not existing_cat:
            db.add(models.Category(**cat))
    db.commit()
    db.close()
    yield


app = FastAPI(title="Udemy Clone API", lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)

# Mount static directory for serving uploads
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# INCLUDE ROUTERS
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(curriculum.router)
app.include_router(services.router)
app.include_router(payments.router)


@app.get("/")
def read_root():
    return {"message": "Udemy Clone Backend is running!"}