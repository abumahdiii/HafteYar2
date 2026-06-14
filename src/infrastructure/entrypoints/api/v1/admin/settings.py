from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.models.settings import SystemSetting, FeatureFlag
from src.infrastructure.entrypoints.schemas.settings_schemas import (
    SystemSettingResponse, SystemSettingUpdateRequest,
    FeatureFlagResponse, FeatureFlagUpdateRequest
)

router = APIRouter(tags=["admin_settings"])

@router.get("/system-settings", response_model=List[SystemSettingResponse])
def get_system_settings(
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    settings = db.query(SystemSetting).all()
    return settings

@router.put("/system-settings/{key}", response_model=SystemSettingResponse)
def update_system_setting(
    key: str,
    request: SystemSettingUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(key=key, value=request.value, description=request.description, is_public=request.is_public or False)
        db.add(setting)
    else:
        setting.value = request.value
        if request.description is not None:
            setting.description = request.description
        if request.is_public is not None:
            setting.is_public = request.is_public
            
    db.commit()
    db.refresh(setting)
    return setting

@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
def get_feature_flags(
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    flags = db.query(FeatureFlag).all()
    return flags

@router.put("/feature-flags/{key}", response_model=FeatureFlagResponse)
def update_feature_flag(
    key: str,
    request: FeatureFlagUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    flag = db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
    if not flag:
        flag = FeatureFlag(key=key, is_enabled=request.is_enabled, description=request.description, conditions=request.conditions)
        db.add(flag)
    else:
        flag.is_enabled = request.is_enabled
        if request.description is not None:
            flag.description = request.description
        if request.conditions is not None:
            flag.conditions = request.conditions
            
    db.commit()
    db.refresh(flag)
    return flag
