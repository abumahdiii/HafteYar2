from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class Feature(BaseModel):
    id: str
    code: str  # e.g., "AI_CHAT", "UNLIMITED_PROJECTS"
    name: str

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: int
    duration_days: int
    features: List[Feature] = []

class Subscription(BaseModel):
    id: str
    team_id: str
    plan_id: str
    starts_at: datetime
    expires_at: datetime
    plan: Optional[SubscriptionPlan] = None
    
    @property
    def is_active(self) -> bool:
        return self.expires_at > datetime.utcnow()
    
    def has_feature(self, feature_code: str) -> bool:
        if not self.is_active or not self.plan:
            return False
        return any(f.code == feature_code for f in self.plan.features)
