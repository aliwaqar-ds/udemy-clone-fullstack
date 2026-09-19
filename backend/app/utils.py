import os
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
import random
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_jwt_key_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


# Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Cloudinary Media Upload Helper ---

# Configure Cloudinary using environment variables from .env
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


async def upload_file_to_cloudinary(file: UploadFile, folder: str = "udemy_clone") -> str:
    """
    Uploads an image or video to Cloudinary and returns its secure public HTTPS URL.
    """
    try:
        response = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="auto"  # Auto-detects image vs video
        )
        return response.get("secure_url")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload media to Cloudinary: {str(e)}"
        )