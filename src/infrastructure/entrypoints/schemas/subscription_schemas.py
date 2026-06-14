from pydantic import BaseModel
from typing import List, Optional

class AssignPlanRequest(BaseModel):
    team_id: str
    plan_id: str

class FeatureCheckResponse(BaseModel):
    team_id: str
    feature_code: str
    has_access: bool

from datetime import datetime

class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    price: int
    duration_days: int

    class Config:
        from_attributes = True

class SubscriptionPlanCreateRequest(BaseModel):
    name: str
    price: int
    duration_days: int

class SubscriptionPlanUpdateRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    duration_days: Optional[int] = None

class SubscriptionResponse(BaseModel):
    id: str
    owner_type: str
    owner_id: str
    plan_id: str
    starts_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True
