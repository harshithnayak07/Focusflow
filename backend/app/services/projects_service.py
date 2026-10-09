from sqlalchemy.orm import Session

from app.models.projects import Project
from app.repositories.projects_respository import create_project_rep
from app.schemas.projects import ProjectCreate


def create_project_service(
    db: Session,
    project: ProjectCreate,
    owner_id: int
):
    db_project = Project(
        name=project.name,
        description=project.description,
        owner_id=owner_id
    )

    return create_project_rep(db, db_project)