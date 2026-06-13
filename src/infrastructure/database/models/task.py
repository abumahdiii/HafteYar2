from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.session import Base
from src.domain.utils.ids import new_task_id, new_assignee_id, new_comment_id
from src.domain.entities.enums import TaskStatus

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String(32), primary_key=True, default=new_task_id)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, nullable=False, default=0)
    
    list_id = Column(String(32), ForeignKey("project_lists.id"), nullable=False)
    project_id = Column(String(32), ForeignKey("projects.id"), nullable=False)
    creator_id = Column(String(32), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    list = relationship("ProjectList", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    creator = relationship("User")
    
    assignees = relationship("TaskAssignee", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")

class TaskAssignee(Base):
    __tablename__ = "task_assignees"
    
    id = Column(String(32), primary_key=True, default=new_assignee_id)
    task_id = Column(String(32), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)

    task = relationship("Task", back_populates="assignees")
    user = relationship("User", back_populates="tasks_assigned")

class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(String(32), primary_key=True, default=new_comment_id)
    task_id = Column(String(32), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    media_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    user = relationship("User")
