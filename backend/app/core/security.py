from fastapi import HTTPException
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
import jwt, os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


password_hash = PasswordHash.recommended()

ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(user_id : str) -> str:
    expire = datetime.now(timezone.utc) + timedelta( minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub" : str(user_id),
        "exp" : expire
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    

def hash_password(password:str) -> str:
    return password_hash.hash(password)

def verify_password(password:str, hashed_password:str):
    return password_hash.verify(password,hashed_password)