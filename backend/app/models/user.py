from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database.connection import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default= "user")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at =Column(DateTime)
    updated_at = Column(DateTime)
    
    projects = relationship("Project", back_populates="owner")
    tasks = relationship("Task", back_populates="owner")