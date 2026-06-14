from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AIProviderCreateRequest(BaseModel):
    name: str
    api_key: str
    base_url: Optional[str] = None
    is_active: bool = True

class AIProviderUpdateRequest(BaseModel):
    name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None

class AIProviderResponse(BaseModel):
    id: str
    name: str
    base_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class AIModelCreateRequest(BaseModel):
    provider_id: str
    name: str
    default_temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: Optional[str] = None
    is_active: bool = True

class AIModelUpdateRequest(BaseModel):
    name: Optional[str] = None
    default_temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None

class AIModelResponse(BaseModel):
    id: str
    provider_id: str
    name: str
    default_temperature: float
    max_tokens: int
    system_prompt: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class AIUsageLogResponse(BaseModel):
    id: str
    conversation_id: Optional[str]
    user_id: Optional[str]
    team_id: Optional[str]
    provider: str
    model: str
    request_type: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    created_at: datetime

    class Config:
        from_attributes = True

class AIUsageLogListResponse(BaseModel):
    items: List[AIUsageLogResponse]
    total: int
