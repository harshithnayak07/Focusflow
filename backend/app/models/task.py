from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_completed = Column(Boolean, default=False, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    project = relationship("Project", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")
