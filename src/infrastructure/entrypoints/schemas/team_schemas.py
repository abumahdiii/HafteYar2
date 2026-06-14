from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TeamCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the team")

class TeamResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    subscription_expiry: datetime
    is_active: bool

    class Config:
        from_attributes = True

class TeamUpdateRequest(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_expiry: Optional[datetime] = None

class TeamListResponse(BaseModel):
    items: List[TeamResponse]
    total: int
