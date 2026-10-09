from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate, Userlogin, Token
from app.core.security import hash_password, verify_password,create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from app.core.dependence import get_current_user
from app.repositories.user_repository import get_all_users, get_user_id, create_user_rep, update_user_name, del_user,get_user_login
from app.services.user_service import create_user_service, login_user_service
router = APIRouter()

@router.get("/me", response_model=UserResponse)
def test(current_user : User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserResponse])
def get_users(db : Session = Depends(get_db)):
    users = get_all_users(db)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id:int, db : Session = Depends(get_db)):
    
    user = get_user_id(user_id,db)
    
    if user is None:
        raise HTTPException(
            status_code= 404,
            detail= "User not found"
        )
    return user

@router.post("/", response_model=UserResponse)
def create_user(user:UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user)
    
    

@router.put("/{user_id}", response_model= UserResponse)
def update_user(user_id:int, user_update:UserUpdate, db:Session = Depends(get_db) ):
    
    user = get_user_id(user_id, db)
    
    if user is None:
        raise HTTPException(
            status_code= 404,
            detail= "User not found"
        )
        
    return update_user_name(db, user, user_update.name)

@router.delete("/{user_id}")
def delete_user(user_id : int, db :Session = Depends(get_db)):
    
    user = get_user_id(user_id, db)
    
    if user is None:
        raise HTTPException(
            status_code= 404,
            detail= "User not found"
        )
        
    del_user(db, user)
    
    return {"message":"User deleted Successfully"}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_user_service(db, form_data.username, form_data.password)