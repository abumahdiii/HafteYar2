from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AIPlanRequest(BaseModel):
    conversation_id: str
    prompt: str

class AIPlanItemSchema(BaseModel):
    id: str
    tool_name: str
    parameters: Dict[str, Any]
    initial_state: str
    final_state: str
    current_version_index: int
    executed: bool

    class Config:
        from_attributes = True

class AIPlanResponse(BaseModel):
    id: str
    status: str
    context_snapshot: Dict[str, Any]
    items: List[AIPlanItemSchema]

    class Config:
        from_attributes = True

class ReviewItemRequest(BaseModel):
    item_id: str
    final_state: str = Field(..., description="GREEN, YELLOW, or RED")
    feedback_text: Optional[str] = None

class UpdatePlanReviewRequest(BaseModel):
    reviews: List[ReviewItemRequest]

class RefinePlanResponse(BaseModel):
    message: str
    refined_items_count: int

class ExecutePlanResponse(BaseModel):
    status: str
    executed_items_count: int
    failed_items_count: int
    details: Dict[str, Any]

class MessageResponse(BaseModel):
    id: str
    role: str
    type: str
    content: Optional[str]
    created_at: Any

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    channel: str
    status: str
    assigned_to: Optional[str]
    tags: Optional[List[str]]
    last_message_at: Any
    created_at: Any

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int

class ConversationUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None

class MessageCreateRequest(BaseModel):
    content: str

