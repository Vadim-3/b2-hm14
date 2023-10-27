from typing import List
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from fast_api_app.database.models import User, UserAuth
from fast_api_app.schemas import UserSchema, UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(UserAuth).filter(UserAuth.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = UserAuth(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_token(user: UserAuth, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def get_users(skip: int, limit: int, user: UserAuth, db: Session) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


async def get_user(user_id: int, user: UserAuth, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()


async def get_birthday(today, end_date, user: UserAuth, db: Session):
    users = db.query(User).all()
    result = []
    for user in users:
        if (
                user.birthday_date.month >= today.month and user.birthday_date.day >= today.day and user.birthday_date.month <= end_date.month and user.birthday_date.day <= end_date.day):
            result.append(user)
    return result


async def search_users(first_name: str | None, last_name: str | None, email: str | None, user: UserAuth, db: Session):
    result = []
    users = db.query(User).all()
    for user in users:
        if first_name != None:
            if user.first_name == first_name:
                result.append(user)
        if last_name != None:
            if user.last_name == last_name:
                result.append(user)
        if email != None:
            if user.email == email:
                result.append(user)
    return result


async def create_users(body: UserSchema, user: UserAuth, db: Session) -> User:
    user_ = User(first_name=body.first_name, last_name=body.last_name, birthday_date=body.birthday_date,
                 email=body.email, phone_numbers=body.phone_numbers, other_description=body.other_description)
    db.add(user_)
    db.commit()
    db.refresh(user_)
    return user_


async def update_user(user_id: int, body: UserSchema, user: UserAuth, db: Session) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.first_name = body.first_name
        user.last_name = body.last_name
        user.phone_numbers = body.phone_numbers
        user.email = body.email
        user.other_description = body.other_description
        db.commit()
    return user


async def remove_user(user_id: int, user: UserAuth, db: Session) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user


async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
