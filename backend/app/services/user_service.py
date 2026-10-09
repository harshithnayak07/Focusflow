from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import create_user_rep
from app.core.security import hash_password
from app.schemas.user import UserCreate


def create_user_service(db: Session, user: UserCreate):
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    return create_user_rep(db, db_user)

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repository import get_user_login
from app.core.security import verify_password, create_access_token


def login_user_service(db: Session, email: str, password: str):
    user = get_user_login(db, email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "Bearer"
    }