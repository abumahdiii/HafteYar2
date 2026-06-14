from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.models.subscription import Subscription, SubscriptionPlan
from src.infrastructure.entrypoints.schemas.subscription_schemas import (
    SubscriptionPlanResponse, SubscriptionPlanCreateRequest, SubscriptionPlanUpdateRequest,
    SubscriptionResponse
)
from src.domain.utils.ids import generate_id

router = APIRouter(prefix="/subscriptions", tags=["admin_subscriptions"])

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
def get_subscription_plans(
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plans = db.query(SubscriptionPlan).all()
    return [SubscriptionPlanResponse.model_validate(p) for p in plans]

@router.post("/plans", response_model=SubscriptionPlanResponse)
def create_subscription_plan(
    request: SubscriptionPlanCreateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    new_plan = SubscriptionPlan(
        id=generate_id("pln"),
        name=request.name,
        price=request.price,
        duration_days=request.duration_days
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return SubscriptionPlanResponse.model_validate(new_plan)

@router.put("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
def update_subscription_plan(
    plan_id: str,
    request: SubscriptionPlanUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    if request.name is not None:
        plan.name = request.name
    if request.price is not None:
        plan.price = request.price
    if request.duration_days is not None:
        plan.duration_days = request.duration_days
        
    db.commit()
    db.refresh(plan)
    return SubscriptionPlanResponse.model_validate(plan)

@router.get("", response_model=List[SubscriptionResponse])
def get_subscriptions(
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    subscriptions = db.query(Subscription).order_by(Subscription.starts_at.desc()).all()
    return [SubscriptionResponse.model_validate(s) for s in subscriptions]
