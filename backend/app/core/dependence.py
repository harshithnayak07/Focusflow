from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from app.core.security import decode_access_token
from app.database.dependencies import get_db
from sqlalchemy.orm import Session
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token : str =Depends(oauth2_scheme), db : Session = Depends(get_db)):
    
    payload = decode_access_token(token)
    
    user_id = int(payload["sub"])
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
        
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user