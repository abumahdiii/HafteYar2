from typing import Optional, List
from sqlalchemy.orm import Session
from src.application.interfaces.repositories import ITeamRepository
from src.domain.entities.team import TeamEntity, TeamMemberEntity
from src.infrastructure.database.models.team import Team, TeamMember

class TeamRepository(ITeamRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: Team) -> TeamEntity:
        return TeamEntity(
            id=model.id,
            name=model.name,
            created_at=model.created_at,
            subscription_expiry=model.subscription_expiry,
            is_active=model.is_active,
            members=[
                TeamMemberEntity(
                    id=mem.id,
                    team_id=mem.team_id,
                    user_id=mem.user_id,
                    role=mem.role,
                    has_ai_access=mem.has_ai_access
                ) for mem in model.members
            ]
        )

    def get_by_id(self, team_id: str) -> Optional[TeamEntity]:
        team_model = self.db.query(Team).filter(Team.id == team_id).first()
        if team_model:
            return self._to_entity(team_model)
        return None

    def get_all_for_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[TeamEntity]:
        team_models = (
            self.db.query(Team)
            .join(TeamMember)
            .filter(TeamMember.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(t) for t in team_models]

    def get_all(self, skip: int = 0, limit: int = 50) -> List[TeamEntity]:
        teams = self.db.query(Team).offset(skip).limit(limit).all()
        return [self._to_entity(t) for t in teams]

    def count(self) -> int:
        return self.db.query(Team).count()

    def create(self, team: TeamEntity) -> TeamEntity:
        team_model = Team(
            id=team.id,
            name=team.name,
            created_at=team.created_at,
            subscription_expiry=team.subscription_expiry,
            is_active=team.is_active
        )
        self.db.add(team_model)
        
        for mem in team.members:
            mem_model = TeamMember(
                id=mem.id,
                team_id=mem.team_id,
                user_id=mem.user_id,
                role=mem.role,
                has_ai_access=mem.has_ai_access
            )
            self.db.add(mem_model)
            
        self.db.commit()
        self.db.refresh(team_model)
        return self._to_entity(team_model)

    def update(self, team: TeamEntity) -> TeamEntity:
        team_model = self.db.query(Team).filter(Team.id == team.id).first()
        if team_model:
            team_model.name = team.name
            team_model.is_active = team.is_active
            team_model.subscription_expiry = team.subscription_expiry
            self.db.commit()
            self.db.refresh(team_model)
            return self._to_entity(team_model)
        return team

    def delete(self, team_id: str) -> None:
        self.db.query(Team).filter(Team.id == team_id).delete()
        self.db.commit()
