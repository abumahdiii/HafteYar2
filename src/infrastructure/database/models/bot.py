from sqlalchemy import Column, String, JSON, DateTime
from datetime import datetime
from src.infrastructure.database.session import Base

class TelegramUserSession(Base):
    __tablename__ = "telegram_user_sessions"

    chat_id = Column(String, primary_key=True, index=True)
    state = Column(String, nullable=False, default="IDLE")
    state_data = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
