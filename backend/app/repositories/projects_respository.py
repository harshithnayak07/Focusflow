from sqlalchemy.orm import Session
from app.models.projects import Project

def create_project_rep(db : Session, db_project : Project):
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def getall_projects(db : Session, owner_id : int):
    return db.query(Project).filter(Project.owner_id == owner_id).all()

def getone_project(db : Session, project_id : int, owner_id : int):
    return db.query(Project).filter(Project.id == project_id, Project.owner_id == owner_id).first()

def update_project_rep(db : Session, project : Project, name : str, description : str | None):
    
    project.name = name
    project.description = description
    
    db.commit()
    db.refresh(project)
    
    return project

def delete_project_rep(db : Session, project : Project):
    db.delete(project)
    db.commit()
    
def get_project_by_owner(
    db: Session,
    project_id: int,
    owner_id: int
):
    return db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == owner_id
    ).first()
    