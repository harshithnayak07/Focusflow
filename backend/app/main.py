from fastapi import FastAPI
from app.models import User, Project, Task
from app.database.connection import Base, engine
from app.routers import users, projects, tasks, admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins =[ "http://127.0.0.2:5500"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(users.router, prefix= "/users", tags= ["users"])
app.include_router(projects.router, prefix= "/projects", tags = ["projects"])
app.include_router(tasks.router, prefix= "/tasks", tags=["tasks"])
app.include_router(admin.router, prefix= "/admin", tags= ["admin"])
