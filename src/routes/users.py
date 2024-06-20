from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.config import settings
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Отримує дані поточного користувача.

    Args:
        current_user (User): Поточний авторизований користувач.

    Returns:
        UserDb: Дані користувача.
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(
        file: UploadFile = File(...),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Оновлює аватар користувача.

    Args:
        file (UploadFile): Файл зображення для аватара.
        current_user (User): Поточний авторизований користувач.
        db (Session): Сеанс бази даних.

    Returns:
        UserDb: Дані користувача з оновленим аватаром.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    upload_result = cloudinary.uploader.upload(
        file.file,
        public_id=f'NotesApp/{current_user.username}',
        overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=upload_result.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
