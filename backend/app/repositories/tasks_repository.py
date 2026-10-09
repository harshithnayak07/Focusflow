from sqlalchemy.orm import Session
from app.models.task import Task

def create_task_rep(db : Session, db_task : Task):
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

def get_all_tasks(db: Session, owner_id: int):
    return db.query(Task).filter(
        Task.owner_id == owner_id
    ).all()
    
def get_task_by_id(
    db: Session,
    task_id: int,
    owner_id: int
):
    return db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == owner_id
    ).first()
    
def update_task_record(
    db: Session,
    task: Task,
    name: str,
    is_completed: bool
):
    task.name = name
    task.is_completed = is_completed

    db.commit()
    db.refresh(task)

    return task

def delete_task(db : Session, task : Task):
    db.delete(task)
    db.commit()
    