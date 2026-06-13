from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from src.domain.entities.enums import TaskStatus

@dataclass
class TaskAssigneeEntity:
    id: str
    task_id: str
    user_id: str

@dataclass
class TaskCommentEntity:
    id: str
    task_id: str
    user_id: str
    content: str
    media_url: Optional[str]
    media_type: Optional[str]
    created_at: datetime

@dataclass
class TaskEntity:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[datetime]
    priority: int
    list_id: str
    project_id: str
    creator_id: Optional[str]
    created_at: datetime
    assignees: List[TaskAssigneeEntity] = field(default_factory=list)
    comments: List[TaskCommentEntity] = field(default_factory=list)
