from typing import Optional
from sqlalchemy.orm import Session
from src.application.interfaces.repositories import SubscriptionRepository
from src.domain.entities.subscription import Subscription as SubscriptionEntity
from src.domain.entities.subscription import SubscriptionPlan as SubscriptionPlanEntity
from src.domain.entities.subscription import Feature as FeatureEntity
from src.infrastructure.database.models.subscription import Subscription, SubscriptionPlan, Feature, PlanFeature
from datetime import datetime

class SQLAlchemySubscriptionRepository(SubscriptionRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_feature_entity(self, feature_model: Feature) -> FeatureEntity:
        return FeatureEntity(
            id=feature_model.id,
            code=feature_model.code,
            name=feature_model.name
        )

    def _to_plan_entity(self, plan_model: SubscriptionPlan) -> SubscriptionPlanEntity:
        features = [self._to_feature_entity(pf.feature) for pf in plan_model.features]
        return SubscriptionPlanEntity(
            id=plan_model.id,
            name=plan_model.name,
            price=plan_model.price,
            duration_days=plan_model.duration_days,
            features=features
        )

    def _to_entity(self, model: Subscription) -> SubscriptionEntity:
        plan_entity = self._to_plan_entity(model.plan) if model.plan else None
        return SubscriptionEntity(
            id=model.id,
            team_id=model.team_id,
            plan_id=model.plan_id,
            starts_at=model.starts_at,
            expires_at=model.expires_at,
            plan=plan_entity
        )

    def get_active_subscription(self, team_id: str) -> Optional[SubscriptionEntity]:
        # Get latest active subscription
        model = self.session.query(Subscription).filter(
            Subscription.team_id == team_id,
            Subscription.expires_at > datetime.utcnow()
        ).order_by(Subscription.expires_at.desc()).first()
        
        if not model:
            return None
            
        return self._to_entity(model)
        
    def create_subscription(self, subscription: SubscriptionEntity) -> SubscriptionEntity:
        model = Subscription(
            id=subscription.id,
            team_id=subscription.team_id,
            plan_id=subscription.plan_id,
            starts_at=subscription.starts_at,
            expires_at=subscription.expires_at
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)
        
    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlanEntity]:
        model = self.session.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not model:
            return None
        return self._to_plan_entity(model)
