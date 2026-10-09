from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependence import get_current_admin
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.repositories.user_repository import get_all_users
from app.repositories.user_repository import (
    get_user_id,
    del_user
)
router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def get_all_users_admin(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return get_all_users(db)

@router.delete("/users/{user_id}")
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = get_user_id(user_id, db)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot delete their own account"
        )

    del_user(db, user)

    return {"message": "User deleted successfully"}