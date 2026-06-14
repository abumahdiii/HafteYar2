from fastapi import APIRouter, Depends
from src.infrastructure.entrypoints.schemas.ai_schemas import (
    AIPlanRequest, AIPlanResponse, UpdatePlanReviewRequest, RefinePlanResponse, ExecutePlanResponse
)
from src.application.ai.middleware import AIMiddleware
from src.application.ai.executor import PlanExecutor
from src.infrastructure.entrypoints.dependencies import get_ai_middleware, get_plan_executor, get_current_user
from src.infrastructure.database.models.ai import ExecutionPlan
from src.domain.exceptions import ResourceNotFoundError


router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/plan", response_model=AIPlanResponse)
def generate_execution_plan(
    request: AIPlanRequest,
    current_user_id: str = Depends(get_current_user),
    middleware: AIMiddleware = Depends(get_ai_middleware)
):
    """
    Generates an ExecutionPlan strictly in PENDING state.
    Does NOT execute any tools directly (Read-only phase).
    """
    # Note: In a robust setup, verify current_user_id has access to conversation_id
    plan = middleware.process_user_input(
        conversation_id=request.conversation_id,
        user_input=request.prompt
    )
    return plan

@router.get("/plan/{plan_id}", response_model=AIPlanResponse)
def get_execution_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user),
    middleware: AIMiddleware = Depends(get_ai_middleware)
):
    plan = middleware.db.query(ExecutionPlan).filter(ExecutionPlan.id == plan_id).first()
    if not plan:
        raise ResourceNotFoundError("Plan not found")
    return plan

@router.patch("/plan/{plan_id}/review", response_model=AIPlanResponse)
def review_execution_plan(
    plan_id: str,
    request: UpdatePlanReviewRequest,
    current_user_id: str = Depends(get_current_user),
    middleware: AIMiddleware = Depends(get_ai_middleware)
):
    reviews = [{"item_id": r.item_id, "final_state": r.final_state, "feedback_text": r.feedback_text} for r in request.reviews]
    plan = middleware.review_plan(plan_id=plan_id, reviews=reviews)
    return plan

@router.post("/plan/{plan_id}/refine", response_model=RefinePlanResponse)
def refine_execution_plan(
    plan_id: str,
    request: UpdatePlanReviewRequest, # We can reuse the review request or just take feedbacks directly. Let's accept feedbacks from DB state or direct.
    current_user_id: str = Depends(get_current_user),
    middleware: AIMiddleware = Depends(get_ai_middleware)
):
    # Map item_id -> feedback_text for items marked YELLOW
    feedbacks = {r.item_id: r.feedback_text for r in request.reviews if r.feedback_text}
    plan, count = middleware.refine_plan(plan_id=plan_id, feedbacks=feedbacks)
    return RefinePlanResponse(message="Refinement complete", refined_items_count=count)

@router.post("/plan/{plan_id}/execute", response_model=ExecutePlanResponse)
def execute_plan(
    plan_id: str,
    current_user_id: str = Depends(get_current_user),
    executor: PlanExecutor = Depends(get_plan_executor)
):
    plan = executor.execute_plan(plan_id=plan_id)
    executed = sum(1 for i in plan.items if i.executed)
    failed = sum(1 for i in plan.items if not i.executed and i.final_state != "RED")
    
    return ExecutePlanResponse(
        status=plan.status,
        executed_items_count=executed,
        failed_items_count=failed,
        details={"total_items": len(plan.items)}
    )
