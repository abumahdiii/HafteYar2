from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime

class SystemSettingResponse(BaseModel):
    key: str
    value: Any
    description: Optional[str]
    is_public: bool
    updated_at: datetime

class SystemSettingUpdateRequest(BaseModel):
    value: Any
    description: Optional[str] = None
    is_public: Optional[bool] = None

class FeatureFlagResponse(BaseModel):
    key: str
    is_enabled: bool
    description: Optional[str]
    conditions: Optional[Dict]
    updated_at: datetime

class FeatureFlagUpdateRequest(BaseModel):
    is_enabled: bool
    description: Optional[str] = None
    conditions: Optional[Dict] = None
