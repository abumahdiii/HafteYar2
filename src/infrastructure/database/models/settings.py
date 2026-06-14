from sqlalchemy import Column, String, Boolean, JSON, DateTime
from datetime import datetime
from src.infrastructure.database.session import Base
from uuid import uuid4

def new_id():
    return uuid4().hex

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(JSON, nullable=False)
    description = Column(String, nullable=True)
    is_public = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    
    key = Column(String, primary_key=True, index=True)
    is_enabled = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    conditions = Column(JSON, nullable=True) # For targeted rollouts (e.g., {"teams": ["id1"], "users": ["id2"]})
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
