from datetime import datetime, timedelta
from typing import List
from src.application.interfaces.repositories import ITeamRepository, IProjectRepository, IListRepository
from src.domain.entities.team import TeamEntity, TeamMemberEntity
from src.domain.entities.project import ProjectEntity, ProjectListEntity
from src.domain.entities.enums import TeamRole
from src.domain.utils.ids import new_team_id, new_member_id, new_project_id, new_list_id
from src.domain.exceptions import AccessDeniedError

class TeamManagementUseCase:
    def __init__(
        self,
        team_repo: ITeamRepository,
        project_repo: IProjectRepository,
        list_repo: IListRepository
    ):
        self.team_repo = team_repo
        self.project_repo = project_repo
        self.list_repo = list_repo

    def create_team(self, name: str, owner_user_id: str) -> TeamEntity:
        """
        Creates a new team and automatically provisions default project and lists.
        """
        team_id = new_team_id()
        created_at = datetime.utcnow()
        subscription_expiry = created_at + timedelta(days=30)
        
        owner_member = TeamMemberEntity(
            id=new_member_id(),
            team_id=team_id,
            user_id=owner_user_id,
            role=TeamRole.OWNER
        )

        team = TeamEntity(
            id=team_id,
            name=name,
            created_at=created_at,
            subscription_expiry=subscription_expiry,
            is_active=True,
            members=[owner_member]
        )

        team = self.team_repo.create(team)
        self._provision_default_workspace(team.id)
        
        return team

    def _provision_default_workspace(self, team_id: str):
        """Creates the default 'پروژه عمومی' and its columns."""
        project = ProjectEntity(
            id=new_project_id(),
            team_id=team_id,
            name="پروژه عمومی",
            description="پروژه پیش‌فرض ساخته شده توسط سیستم",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            lists=[]
        )
        self.project_repo.create(project)
        
        default_lists = ["انجام نشده", "در حال انجام", "انجام شده"]
        for idx, lst_name in enumerate(default_lists):
            lst_entity = ProjectListEntity(
                id=new_list_id(),
                project_id=project.id,
                name=lst_name,
                position=idx,
                created_at=datetime.utcnow()
            )
            self.list_repo.create(lst_entity)

    def get_user_teams(self, user_id: str) -> List[TeamEntity]:
        return self.team_repo.get_all_for_user(user_id)

    def ensure_team_subscription_valid(self, team_id: str):
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise AccessDeniedError("Team not found.")
        if not team.is_subscription_valid:
            raise AccessDeniedError("Team subscription has expired or is inactive.")
