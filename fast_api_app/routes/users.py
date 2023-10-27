from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import date, timedelta
from fast_api_app.database.connect_db import get_db
from fast_api_app.schemas import UserSchema, UserResponse, UserDb
from fast_api_app.repository import users as repository_users
from fast_api_app.database.models import User, UserAuth
from fast_api_app.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix='/users', tags=["users"])


@router.get("/", response_model=List[UserResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: UserAuth = Depends(auth_service.get_current_user)):
    users = await repository_users.get_users(skip, limit, current_user, db)
    return users


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    cloudinary.config(
        cloud_name="dmybldclv",
        api_key="592143484358843",
        api_secret="YqKAI25KSkQ9UwyWxPn_gcwX-3A",
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.get("/birthdays", response_model=List[UserResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_birthdays(db: Session = Depends(get_db),
                         current_user: UserAuth = Depends(auth_service.get_current_user)):
    today = date.today()
    end_date = today + timedelta(days=7)
    birthdays = await repository_users.get_birthday(today, end_date, current_user, db)
    if birthdays is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return birthdays


@router.get("/search", response_model=List[UserResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search(db: Session = Depends(get_db), current_user: UserAuth = Depends(auth_service.get_current_user),
                 first_name: str = Query(None), last_name: str = Query(None), email: str = Query(None)):
    users = await repository_users.search_users(first_name, last_name, email, current_user, db)
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return users


@router.get("/{user_id}", response_model=UserResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_user(user_id: int, db: Session = Depends(get_db),
                    current_user: UserAuth = Depends(auth_service.get_current_user)):
    users = await repository_users.get_user(user_id, current_user, db)
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_users(body: UserSchema, db: Session = Depends(get_db),
                       current_user: UserAuth = Depends(auth_service.get_current_user)):
    return await repository_users.create_users(body, current_user, db)


@router.put("/{user_id}", response_model=UserResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_user(body: UserSchema, user_id: int, db: Session = Depends(get_db),
                      current_user: UserAuth = Depends(auth_service.get_current_user)):
    user = await repository_users.update_user(user_id, body, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=UserResponse, description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_user(user_id: int, db: Session = Depends(get_db),
                      current_user: UserAuth = Depends(auth_service.get_current_user)):
    user = await repository_users.remove_user(user_id, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user