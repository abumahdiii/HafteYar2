from pydantic import BaseModel
from typing import List, Optional

class AssignPlanRequest(BaseModel):
    team_id: str
    plan_id: str

class FeatureCheckResponse(BaseModel):
    team_id: str
    feature_code: str
    has_access: bool
