from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from src.infrastructure.database.session import Base
from src.domain.utils.ids import new_team_id, new_member_id
from src.domain.entities.enums import TeamRole

def get_default_subscription_expiry():
    return datetime.utcnow() + timedelta(days=30)

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(String(32), primary_key=True, default=new_team_id)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_expiry = Column(DateTime, default=get_default_subscription_expiry)
    is_active = Column(Boolean, default=True)
    ai_execution_mode = Column(String, default="ALWAYS_REVIEW") # ALWAYS_REVIEW, REVIEW_CRITICAL_ONLY, AUTO_EXECUTE

    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="team", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String(32), primary_key=True, default=new_member_id)
    team_id = Column(String(32), ForeignKey("teams.id"), nullable=False, index=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(SAEnum(TeamRole), nullable=False, default=TeamRole.MEMBER)
    has_ai_access = Column(Boolean, default=False)

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")
