from datetime import datetime, timedelta
from src.application.interfaces.repositories import SubscriptionRepository
from src.domain.entities.subscription import Subscription
from src.domain.exceptions import ResourceNotFoundError
from src.domain.utils.ids import generate_id

class SubscriptionUseCase:
    def __init__(self, subscription_repo: SubscriptionRepository):
        self.subscription_repo = subscription_repo

    def has_feature(self, team_id: str, feature_code: str) -> bool:
        """
        Check if a team has an active subscription that includes the specified feature code.
        """
        subscription = self.subscription_repo.get_active_subscription(team_id)
        if not subscription:
            return False
        return subscription.has_feature(feature_code)

    def assign_plan(self, team_id: str, plan_id: str) -> Subscription:
        """
        Assign a subscription plan to a team.
        """
        plan = self.subscription_repo.get_plan(plan_id)
        if not plan:
            raise ResourceNotFoundError(f"Subscription plan {plan_id} not found.")

        starts_at = datetime.utcnow()
        expires_at = starts_at + timedelta(days=plan.duration_days)

        subscription = Subscription(
            id=generate_id("sub"),
            team_id=team_id,
            plan_id=plan.id,
            starts_at=starts_at,
            expires_at=expires_at,
            plan=plan
        )

        return self.subscription_repo.create_subscription(subscription)
