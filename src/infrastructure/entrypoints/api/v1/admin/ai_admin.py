from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.models.ai_settings import AIProvider, AIModel
from src.infrastructure.database.models.usage import AIUsageLog
from src.infrastructure.entrypoints.schemas.ai_admin_schemas import (
    AIProviderResponse, AIProviderCreateRequest, AIProviderUpdateRequest,
    AIModelResponse, AIModelCreateRequest, AIModelUpdateRequest,
    AIUsageLogResponse, AIUsageLogListResponse
)
from src.domain.utils.ids import generate_id

router = APIRouter(prefix="/ai", tags=["admin_ai"])

# --- Providers ---
@router.get("/providers", response_model=List[AIProviderResponse])
def get_providers(
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    providers = db.query(AIProvider).all()
    return [AIProviderResponse.model_validate(p) for p in providers]

@router.post("/providers", response_model=AIProviderResponse)
def create_provider(
    request: AIProviderCreateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    new_provider = AIProvider(
        id=generate_id("prv"),
        name=request.name,
        api_key=request.api_key,
        base_url=request.base_url,
        is_active=request.is_active
    )
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return AIProviderResponse.model_validate(new_provider)

@router.put("/providers/{provider_id}", response_model=AIProviderResponse)
def update_provider(
    provider_id: str,
    request: AIProviderUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    if request.name is not None:
        provider.name = request.name
    if request.api_key is not None:
        provider.api_key = request.api_key
    if request.base_url is not None:
        provider.base_url = request.base_url
    if request.is_active is not None:
        provider.is_active = request.is_active
        
    db.commit()
    db.refresh(provider)
    return AIProviderResponse.model_validate(provider)

# --- Models ---
@router.get("/models", response_model=List[AIModelResponse])
def get_models(
    provider_id: Optional[str] = None,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(AIModel)
    if provider_id:
        query = query.filter(AIModel.provider_id == provider_id)
    models = query.all()
    return [AIModelResponse.model_validate(m) for m in models]

@router.post("/models", response_model=AIModelResponse)
def create_model(
    request: AIModelCreateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    new_model = AIModel(
        id=generate_id("mod"),
        provider_id=request.provider_id,
        name=request.name,
        default_temperature=request.default_temperature,
        max_tokens=request.max_tokens,
        system_prompt=request.system_prompt,
        is_active=request.is_active
    )
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return AIModelResponse.model_validate(new_model)

@router.put("/models/{model_id}", response_model=AIModelResponse)
def update_model(
    model_id: str,
    request: AIModelUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
        
    if request.name is not None:
        model.name = request.name
    if request.default_temperature is not None:
        model.default_temperature = request.default_temperature
    if request.max_tokens is not None:
        model.max_tokens = request.max_tokens
    if request.system_prompt is not None:
        model.system_prompt = request.system_prompt
    if request.is_active is not None:
        model.is_active = request.is_active
        
    db.commit()
    db.refresh(model)
    return AIModelResponse.model_validate(model)

# --- Usage Logs ---
@router.get("/usage", response_model=AIUsageLogListResponse)
def get_usage_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    provider: Optional[str] = None,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(AIUsageLog)
    if provider:
        query = query.filter(AIUsageLog.provider == provider)
        
    total = query.count()
    logs = query.order_by(AIUsageLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return AIUsageLogListResponse(
        items=[AIUsageLogResponse.model_validate(log) for log in logs],
        total=total
    )
