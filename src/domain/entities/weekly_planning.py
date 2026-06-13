from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from src.domain.utils.ids import generate_id

class WeeklyGoal(BaseModel):
    id: str
    team_id: str
    project_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str = "PENDING" # PENDING, IN_PROGRESS, COMPLETED
    created_at: datetime = datetime.utcnow()
    
class WeeklyReport(BaseModel):
    id: str
    team_id: str
    week_start: datetime
    week_end: datetime
    summary: str
    created_at: datetime = datetime.utcnow()
