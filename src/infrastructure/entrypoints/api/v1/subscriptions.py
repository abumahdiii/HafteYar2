from fastapi import APIRouter, Depends
from src.infrastructure.entrypoints.schemas.subscription_schemas import AssignPlanRequest, FeatureCheckResponse
from src.application.use_cases.subscription import SubscriptionUseCase
from src.infrastructure.entrypoints.dependencies import get_subscription_use_case, get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/assign")
def assign_plan(
    request: AssignPlanRequest,
    current_user_id: str = Depends(get_current_user),
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    # In a real system, we'd verify current_user_id is the owner of the team
    sub = use_case.assign_plan(team_id=request.team_id, plan_id=request.plan_id)
    return {"message": "Plan assigned successfully", "subscription_id": sub.id}

@router.get("/check-feature", response_model=FeatureCheckResponse)
def check_feature(
    team_id: str,
    feature_code: str,
    current_user_id: str = Depends(get_current_user),
    use_case: SubscriptionUseCase = Depends(get_subscription_use_case)
):
    has_access = use_case.has_feature(team_id=team_id, feature_code=feature_code)
    return FeatureCheckResponse(team_id=team_id, feature_code=feature_code, has_access=has_access)
