from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union

class AIRequest(BaseModel):
    source: str = Field(..., description="Platform name, e.g., 'telegram', 'bale'")
    chat_id: str = Field(..., description="External chat identifier")
    user_id: Optional[str] = Field(None, description="External user identifier if different from chat_id")
    username: Optional[str] = Field(None, description="External username")
    payload: str = Field(..., description="Message text or command (e.g., '/start', '/execute')")
    is_callback: bool = Field(False, description="True if payload is from an inline button callback")
    callback_id: Optional[str] = Field(None, description="Callback query ID for answering")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context (timestamps, update_id, etc.)")

class InlineButton(BaseModel):
    text: str
    callback_data: str

class GatewayResponse(BaseModel):
    text: str = Field(..., description="The text response to send back to the user")
    buttons: Optional[List[List[str]]] = Field(None, description="A 2D array of strings representing keyboard buttons")
    inline_buttons: Optional[List[List[InlineButton]]] = Field(None, description="A 2D array of inline buttons")
    is_pro_upsell: bool = Field(False, description="True if this message is a Pro upsell message")

