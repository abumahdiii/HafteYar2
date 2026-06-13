from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.session import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    channel = Column(String)  # telegram, bale, web
    active_team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    active_project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    active_member_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    execution_plans = relationship("ExecutionPlan", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    role = Column(String)  # user, assistant, system, tool
    type = Column(String, default="TEXT")  # TEXT, VOICE, IMAGE
    content = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True) # file identifiers, transcriptions
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

class AIToolExecution(Base):
    __tablename__ = "ai_tool_executions"
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    tool_name = Column(String, index=True)
    input_parameters = Column(JSON)
    execution_result = Column(JSON, nullable=True)
    success = Column(Boolean)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExecutionPlan(Base):
    __tablename__ = "execution_plans"
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    
    # Context Snapshot to prevent race conditions during approval
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    member_id = Column(String, ForeignKey("users.id"), nullable=True)
    context_snapshot = Column(JSON) # e.g. {"team_id": 5, "project_id": 12, "member_id": 33}
    
    status = Column(String, default="PENDING") # PENDING, APPROVED, EXECUTED
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    
    conversation = relationship("Conversation", back_populates="execution_plans")
    items = relationship("ExecutionPlanItem", back_populates="plan", cascade="all, delete-orphan")

class ExecutionPlanItem(Base):
    __tablename__ = "execution_plan_items"
    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("execution_plans.id"), index=True)
    tool_name = Column(String)
    parameters = Column(JSON)
    
    # Refinement Tracking for YELLOW state iterations
    refinement_history = Column(JSON, nullable=True) # e.g. [{"timestamp": "...", "reason": "...", "previous_version": "...", "new_version": "..."}]
    
    initial_state = Column(String, default="GREEN") # GREEN, YELLOW, RED
    final_state = Column(String, default="GREEN")
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plan = relationship("ExecutionPlan", back_populates="items")
