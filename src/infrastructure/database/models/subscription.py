from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database.session import Base

class Feature(Base):
    __tablename__ = "features"
    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # e.g. "AI_CHAT"
    name = Column(String)

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    price = Column(Integer)
    duration_days = Column(Integer)
    
    features = relationship("PlanFeature", back_populates="plan")

class PlanFeature(Base):
    __tablename__ = "plan_features"
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"))
    feature_id = Column(String, ForeignKey("features.id"))
    
    plan = relationship("SubscriptionPlan", back_populates="features")
    feature = relationship("Feature")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("teams.id"), index=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"))
    starts_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    team = relationship("Team", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan")
