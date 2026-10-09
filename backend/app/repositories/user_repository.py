from sqlalchemy.orm import Session
from app.models.user import User
from app.models.projects import Project
from app.models.task import Task
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def get_all_users(db : Session):
    return db.query(User).all()

def get_user_id(user_id : int, db:Session):
    return db.query(User).filter(User.id == user_id).first()

def create_user_rep(db : Session, db_user : User):
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    except IntegrityError:
        db.rollback()
        
        raise HTTPException(
            status_code= 409,
            detail= "Email already registered"
        )

def update_user_name(db : Session, user : User, new_name : str):
    user.name = new_name
    db.commit()
    db.refresh(user)
    return user

def count_user_content(db : Session, user_id : int):
    projects = db.query(Project).filter(Project.owner_id == user_id).count()
    tasks = db.query(Task).filter(Task.owner_id == user_id).count()
    return projects, tasks

def del_user(db : Session, user : User):
    projects, tasks = count_user_content(db, user.id)

    if projects or tasks:
        raise HTTPException(
            status_code= 409,
            detail= "User still has projects or tasks"
        )

    try:
        db.delete(user)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code= 409,
            detail= "User still has projects or tasks"
        )
    
def get_user_login(db : Session, email : str):
    return db.query(User).filter(User.email == email).first()