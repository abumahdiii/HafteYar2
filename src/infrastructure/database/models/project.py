from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.session import Base
from src.domain.utils.ids import new_project_id, new_list_id

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(32), primary_key=True, default=new_project_id)
    team_id = Column(String(32), ForeignKey("teams.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="projects")
    lists = relationship("ProjectList", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class ProjectList(Base):
    __tablename__ = "project_lists"
    
    id = Column(String(32), primary_key=True, default=new_list_id)
    project_id = Column(String(32), ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    project = relationship("Project", back_populates="lists")
    tasks = relationship("Task", back_populates="list", cascade="all, delete-orphan")
