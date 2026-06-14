from fastapi import APIRouter, Depends
from typing import List
from src.infrastructure.entrypoints.schemas.team_schemas import TeamCreateRequest, TeamResponse
from src.application.use_cases.team_management import TeamManagementUseCase
from src.infrastructure.entrypoints.dependencies import get_team_use_case, get_current_user

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("", response_model=TeamResponse)
def create_team(
    request: TeamCreateRequest,
    current_user_id: str = Depends(get_current_user),
    use_case: TeamManagementUseCase = Depends(get_team_use_case)
):
    team = use_case.create_team(name=request.name, owner_user_id=current_user_id)
    return team

@router.get("", response_model=List[TeamResponse])
def get_my_teams(
    current_user_id: str = Depends(get_current_user),
    use_case: TeamManagementUseCase = Depends(get_team_use_case)
):
    return use_case.get_user_teams(user_id=current_user_id)
