from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class InternalMessage:
    user_id: str
    message_text: str
    message_id: Optional[str]
    timestamp: datetime
    platform: str
    raw_payload: Dict[str, Any]
    contact_phone: Optional[str] = None

class WebhookAdapter:
    """Unified adapter for both Telegram and Bale (since Bale mimics Telegram's API)."""
    
    def __init__(self, platform: str):
        self.platform = platform

    def parse(self, payload: Dict[str, Any]) -> Optional[InternalMessage]:
        message = payload.get("message") or payload.get("edited_message")
        if not message:
            return None
            
        sender = message.get("from", {})
        user_id = str(sender.get("id"))
        if not user_id:
            return None
            
        text = message.get("text", "")
        msg_id = str(message.get("message_id"))
        timestamp = datetime.utcfromtimestamp(message.get("date", datetime.utcnow().timestamp()))
        
        contact_phone = None
        contact = message.get("contact")
        if contact:
            contact_user_id = str(contact.get("user_id"))
            if contact_user_id == user_id:
                contact_phone = contact.get("phone_number")
                
        return InternalMessage(
            user_id=user_id,
            message_text=text,
            message_id=msg_id,
            timestamp=timestamp,
            platform=self.platform,
            raw_payload=payload,
            contact_phone=contact_phone
        )
