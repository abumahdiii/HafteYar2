from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.models.ai import Conversation, ChatMessage
from src.infrastructure.entrypoints.schemas.ai_schemas import (
    ConversationResponse, ConversationListResponse, ConversationUpdateRequest,
    MessageResponse, MessageCreateRequest
)
from src.domain.utils.ids import generate_id

router = APIRouter(prefix="/conversations", tags=["admin_conversations"])

@router.get("", response_model=ConversationListResponse)
def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Conversation)
    if status:
        query = query.filter(Conversation.status == status)
    
    total = query.count()
    conversations = query.order_by(Conversation.last_message_at.desc()).offset(skip).limit(limit).all()
    
    return ConversationListResponse(
        items=[ConversationResponse.model_validate(c) for c in conversations],
        total=total
    )

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: str,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).order_by(ChatMessage.created_at.asc()).all()
    return [MessageResponse.model_validate(m) for m in messages]

@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    request: ConversationUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if request.status is not None:
        conversation.status = request.status
    if request.assigned_to is not None:
        conversation.assigned_to = request.assigned_to
    if request.tags is not None:
        conversation.tags = request.tags
        
    db.commit()
    db.refresh(conversation)
    return ConversationResponse.model_validate(conversation)

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def add_admin_message(
    conversation_id: str,
    request: MessageCreateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # We add message as "assistant" role or "admin". "assistant" works fine for user interface.
    new_message = ChatMessage(
        id=generate_id("msg"),
        conversation_id=conversation_id,
        role="assistant",
        type="TEXT",
        content=request.content,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    conversation.last_message_at = datetime.utcnow()
    # Change status to pending or open if needed. Usually if admin replies, it is awaiting user.
    db.commit()
    db.refresh(new_message)
    
    return MessageResponse.model_validate(new_message)
