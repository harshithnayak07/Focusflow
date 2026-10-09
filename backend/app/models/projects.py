from sqlalchemy import Column, String, Integer,DateTime, ForeignKey
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")