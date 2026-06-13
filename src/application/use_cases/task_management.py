from datetime import datetime
from typing import List, Optional
from src.application.interfaces.repositories import ITaskRepository, IProjectRepository, ITeamRepository
from src.domain.entities.task import TaskEntity
from src.domain.entities.enums import TaskStatus
from src.domain.utils.ids import new_task_id
from src.domain.exceptions import AccessDeniedError, ResourceNotFoundError

class TaskManagementUseCase:
    def __init__(
        self,
        task_repo: ITaskRepository,
        project_repo: IProjectRepository,
        team_repo: ITeamRepository
    ):
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.team_repo = team_repo

    def _ensure_access(self, project_id: str):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project not found.")
        
        team = self.team_repo.get_by_id(project.team_id)
        if not team:
            raise ResourceNotFoundError("Team not found.")
            
        if not team.is_subscription_valid:
            raise AccessDeniedError("Team subscription has expired or is inactive.")

    def create_task(self, title: str, list_id: str, project_id: str, creator_id: str, description: Optional[str] = None, priority: int = 0) -> TaskEntity:
        self._ensure_access(project_id)

        task = TaskEntity(
            id=new_task_id(),
            title=title,
            description=description,
            status=TaskStatus.TODO,
            due_date=None,
            priority=priority,
            list_id=list_id,
            project_id=project_id,
            creator_id=creator_id,
            created_at=datetime.utcnow()
        )
        return self.task_repo.create(task)

    def get_tasks_for_project(self, project_id: str) -> List[TaskEntity]:
        self._ensure_access(project_id)
        return self.task_repo.get_all_for_project(project_id)

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> TaskEntity:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task not found.")
            
        self._ensure_access(task.project_id)
        task.status = new_status
        return self.task_repo.update(task)
