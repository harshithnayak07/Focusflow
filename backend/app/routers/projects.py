from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.projects import Project
from app.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from app.core.dependence import get_current_user
from app.models.user import User
from app.repositories.projects_respository import create_project_rep, getall_projects, getone_project, update_project_rep, delete_project_rep
from app.services.projects_service import create_project_service
router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_post(
    project : ProjectCreate ,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
    
):
    return create_project_service(
        db,
        project,
        current_user.id
    )
    

@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    return getall_projects(db, current_user.id)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_one(
    project_id : int,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user),
):
    
    project = getone_project(db, project_id, current_user.id)
    
    if project is None:
        raise HTTPException(
            status_code= 404,
            detail= "Project not found"
        )
        
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id : int,
    project_data : ProjectUpdate,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    project = getone_project(db, project_id, current_user.id)
    
    if project is None:
        raise HTTPException(
            status_code= 404,
            detail= "Project not found"
        )
        
    return update_project_rep(
        db,
        project,
        project_data.name,
        project_data.description
    )
    

@router.delete("/{project_id}")
def delete_project(
    project_id : int,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    project = getone_project(db, project_id, current_user.id)
    
    if project is None:
        raise HTTPException(
            status_code= 404,
            detail= "Project not found"
        )
        
    delete_project_rep(db, project)
    
    return {"message":"project deleted Successfully"}