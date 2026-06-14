from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from datetime import datetime
from src.infrastructure.database.session import Base
from src.domain.utils.ids import new_usage_log_id

class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    
    id = Column(String(32), primary_key=True, default=new_usage_log_id)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True, nullable=True)
    user_id = Column(String(32), ForeignKey("users.id"), index=True)
    team_id = Column(String(32), ForeignKey("teams.id"), index=True, nullable=True)
    
    provider = Column(String, index=True) # e.g., openai, anthropic
    model = Column(String, index=True) # e.g., gpt-4o
    request_type = Column(String) # e.g., 'chat', 'tool_execution', 'planner'
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    cost = Column(Float, default=0.0) # Approximate cost in USD or Tomans
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
