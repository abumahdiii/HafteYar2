from typing import Optional, List
from sqlalchemy.orm import Session
from src.application.interfaces.repositories import IProjectRepository, IListRepository
from src.domain.entities.project import ProjectEntity, ProjectListEntity
from src.infrastructure.database.models.project import Project, ProjectList

class ProjectRepository(IProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: Project) -> ProjectEntity:
        return ProjectEntity(
            id=model.id,
            team_id=model.team_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            lists=[
                ProjectListEntity(
                    id=lst.id,
                    project_id=lst.project_id,
                    name=lst.name,
                    position=lst.position,
                    created_at=lst.created_at
                ) for lst in model.lists
            ]
        )

    def get_by_id(self, project_id: str) -> Optional[ProjectEntity]:
        model = self.db.query(Project).filter(Project.id == project_id).first()
        if model:
            return self._to_entity(model)
        return None

    def create(self, project: ProjectEntity) -> ProjectEntity:
        model = Project(
            id=project.id,
            team_id=project.team_id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

class ListRepository(IListRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, lst: ProjectListEntity) -> ProjectListEntity:
        model = ProjectList(
            id=lst.id,
            project_id=lst.project_id,
            name=lst.name,
            position=lst.position,
            created_at=lst.created_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        
        return ProjectListEntity(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            position=model.position,
            created_at=model.created_at
        )
