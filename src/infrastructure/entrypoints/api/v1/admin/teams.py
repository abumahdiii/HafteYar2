from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.repositories.team_repository import TeamRepository
from src.infrastructure.entrypoints.schemas.team_schemas import TeamListResponse, TeamResponse, TeamCreateRequest, TeamUpdateRequest
from src.domain.entities.team import TeamEntity
from src.domain.utils.ids import new_team_id
from datetime import datetime, timedelta

router = APIRouter(prefix="/teams", tags=["admin_teams"])

@router.get("", response_model=TeamListResponse)
def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = TeamRepository(db)
    teams = repo.get_all(skip=skip, limit=limit)
    total = repo.count()
    return TeamListResponse(
        items=[TeamResponse(
            id=t.id, name=t.name, created_at=t.created_at,
            subscription_expiry=t.subscription_expiry, is_active=t.is_active
        ) for t in teams],
        total=total
    )

@router.post("", response_model=TeamResponse)
def create_team(
    request: TeamCreateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = TeamRepository(db)
    new_team = TeamEntity(
        id=new_team_id(),
        name=request.name,
        created_at=datetime.utcnow(),
        subscription_expiry=datetime.utcnow() + timedelta(days=30),
        is_active=True,
        members=[]
    )
    created = repo.create(new_team)
    return TeamResponse(
        id=created.id, name=created.name, created_at=created.created_at,
        subscription_expiry=created.subscription_expiry, is_active=created.is_active
    )

@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    request: TeamUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = TeamRepository(db)
    team = repo.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
        
    if request.name is not None:
        team.name = request.name
    if request.is_active is not None:
        team.is_active = request.is_active
    if request.subscription_expiry is not None:
        team.subscription_expiry = request.subscription_expiry
        
    updated = repo.update(team)
    return TeamResponse(
        id=updated.id, name=updated.name, created_at=updated.created_at,
        subscription_expiry=updated.subscription_expiry, is_active=updated.is_active
    )

@router.delete("/{team_id}")
def delete_team(
    team_id: str,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = TeamRepository(db)
    repo.delete(team_id)
    return {"message": "Team deleted"}
