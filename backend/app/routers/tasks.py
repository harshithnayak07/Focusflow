from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.task import Task
from app.schemas.tasks import CreateTask , TaskResponse, TaskUpdate
from app.models.user import User
from app.models.projects import Project
from app.core.dependence import get_current_user
from app.repositories.projects_respository import get_project_by_owner
from app.repositories.tasks_repository import create_task_rep, get_all_tasks, get_task_by_id, update_task_record, delete_task
from app.services.tasks_service import create_task_service
router = APIRouter()

@router.post("/", response_model=TaskResponse)
def create_task(
    task : CreateTask,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
): 
    return create_task_service(
        db,
        task,
        current_user.id
    )

@router.get("/", response_model= list[TaskResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    return get_all_tasks(
    db,
    current_user.id
)

@router.get("/{task_id}", response_model= TaskResponse)
def get_one(
    task_id : int,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    task = get_task_by_id(
    db,
    task_id,
    current_user.id
)
    
    if task is None:
        raise HTTPException(
            status_code= 404,
            detail= "task not found"
        )
        
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id : int,
    task_data: TaskUpdate,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    task = get_task_by_id(
    db,
    task_id,
    current_user.id
)
    
    if task is None:
        raise HTTPException(
            status_code= 404,
            detail= "task not found"
        )
    return update_task_record(
        db,
        task,
        task_data.name,
        task_data.is_completed
    )
        
    
@router.delete("/{task_id}")
def del_task(
    task_id : int,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    task = get_task_by_id(
    db,
    task_id,
    current_user.id
)
    
    if task is None:
        raise HTTPException(
            status_code= 404,
            detail="task not found"
        )
        
    delete_task(db, task)
    
    return {"message" : "Task deleted Successfully"}