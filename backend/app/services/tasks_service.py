from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.projects_respository import get_project_by_owner
from app.repositories.tasks_repository import create_task_rep
from app.schemas.tasks import CreateTask


def create_task_service(
    db: Session,
    task: CreateTask,
    owner_id: int
):
    project = get_project_by_owner(
        db,
        task.project_id,
        owner_id
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    db_task = Task(
        name=task.name,
        project_id=task.project_id,
        owner_id=owner_id
    )

    return create_task_rep(db, db_task)