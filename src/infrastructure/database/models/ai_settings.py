from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.session import Base
from src.domain.utils.ids import new_provider_id, new_model_id

class AIProvider(Base):
    __tablename__ = "ai_providers"
    
    id = Column(String(32), primary_key=True, default=new_provider_id)
    name = Column(String, unique=True, index=True) # e.g., openai, anthropic, azure
    base_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    models = relationship("AIModel", back_populates="provider")

class AIModel(Base):
    __tablename__ = "ai_models"
    
    id = Column(String(32), primary_key=True, default=new_model_id)
    provider_id = Column(String(32), ForeignKey("ai_providers.id"), index=True)
    service_name = Column(String, index=True) # e.g., 'planner', 'coder', 'chat'
    model_name = Column(String) # e.g., 'gpt-4o', 'claude-3-opus'
    
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    system_prompt = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    provider = relationship("AIProvider", back_populates="models")
