from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.domain.entities.enums import TaskStatus

class TaskCreateRequest(BaseModel):
    title: str
    list_id: str
    project_id: str
    description: Optional[str] = None
    priority: int = 0

class TaskUpdateStatusRequest(BaseModel):
    status: TaskStatus

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: int
    list_id: str
    project_id: str
    creator_id: str
    created_at: datetime
    due_date: Optional[datetime]

    class Config:
        from_attributes = True

from typing import List
class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
