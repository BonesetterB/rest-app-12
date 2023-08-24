from fastapi import APIRouter, Depends,  UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.model import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import config
from src.schemas import UserResponseSchema

router = APIRouter(prefix="/users", tags=["users"])

cloudinary.config(
        cloud_name=config.cloudinary_name,
        api_key=config.cloudinary_api_key,
        api_secret=config.cloudinary_api_secret,
        secure=True
    )

@router.get("/me/", response_model=UserResponseSchema)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Get user details for the currently authenticated user.

    :param current_user: Current authenticated user.
    :type current_user: User
    :return: User details.
    :rtype: UserResponseSchema
    """
    return current_user


@router.patch('/avatar', response_model=UserResponseSchema)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: AsyncSession = Depends(get_db)):

    """
    Update the avatar of the currently authenticated user.

    :param file: Uploaded image file.
    :type file: UploadFile
    :param current_user: Current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: AsyncSession
    :return: Updated user details with the new avatar URL.
    :rtype: UserResponseSchema
    """
    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user