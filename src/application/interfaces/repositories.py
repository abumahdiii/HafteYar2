from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.user import UserEntity
from src.domain.entities.team import TeamEntity
from src.domain.entities.project import ProjectEntity, ProjectListEntity
from src.domain.entities.task import TaskEntity
from src.domain.entities.subscription import Subscription, SubscriptionPlan

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserEntity]:
        pass
        
    @abstractmethod
    def get_by_phone(self, phone: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 50) -> List[UserEntity]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

class ITeamRepository(ABC):
    @abstractmethod
    def get_by_id(self, team_id: str) -> Optional[TeamEntity]:
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 50) -> List[TeamEntity]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def get_all_for_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[TeamEntity]:
        pass

    @abstractmethod
    def create(self, team: TeamEntity) -> TeamEntity:
        pass

    @abstractmethod
    def update(self, team: TeamEntity) -> TeamEntity:
        pass

    @abstractmethod
    def delete(self, team_id: str) -> None:
        pass

class IProjectRepository(ABC):
    @abstractmethod
    def get_by_id(self, project_id: str) -> Optional[ProjectEntity]:
        pass

    @abstractmethod
    def create(self, project: ProjectEntity) -> ProjectEntity:
        pass

class IListRepository(ABC):
    @abstractmethod
    def create(self, lst: ProjectListEntity) -> ProjectListEntity:
        pass

class ITaskRepository(ABC):
    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[TaskEntity]:
        pass

    @abstractmethod
    def get_all_for_project(self, project_id: str, limit: int = 50, offset: int = 0) -> List[TaskEntity]:
        pass

    @abstractmethod
    def create(self, task: TaskEntity) -> TaskEntity:
        pass

    @abstractmethod
    def update(self, task: TaskEntity) -> TaskEntity:
        pass

    @abstractmethod
    def delete(self, task_id: str) -> None:
        pass

class SubscriptionRepository(ABC):
    @abstractmethod
    def get_active_subscription(self, team_id: str) -> Optional[Subscription]:
        pass
    
    @abstractmethod
    def create_subscription(self, subscription: Subscription) -> Subscription:
        pass
    
    @abstractmethod
    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        pass
