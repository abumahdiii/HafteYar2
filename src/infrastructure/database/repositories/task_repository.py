from typing import Optional, List
from sqlalchemy.orm import Session
from src.application.interfaces.repositories import ITaskRepository
from src.domain.entities.task import TaskEntity, TaskAssigneeEntity, TaskCommentEntity
from src.infrastructure.database.models.task import Task, TaskAssignee, TaskComment

class TaskRepository(ITaskRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: Task) -> TaskEntity:
        return TaskEntity(
            id=model.id,
            title=model.title,
            description=model.description,
            status=model.status,
            due_date=model.due_date,
            priority=model.priority,
            list_id=model.list_id,
            project_id=model.project_id,
            creator_id=model.creator_id,
            created_at=model.created_at,
            assignees=[
                TaskAssigneeEntity(
                    id=asn.id,
                    task_id=asn.task_id,
                    user_id=asn.user_id
                ) for asn in model.assignees
            ],
            comments=[
                TaskCommentEntity(
                    id=cmt.id,
                    task_id=cmt.task_id,
                    user_id=cmt.user_id,
                    content=cmt.content,
                    media_url=cmt.media_url,
                    media_type=cmt.media_type,
                    created_at=cmt.created_at
                ) for cmt in model.comments
            ]
        )

    def get_by_id(self, task_id: str) -> Optional[TaskEntity]:
        model = self.db.query(Task).filter(Task.id == task_id).first()
        if model:
            return self._to_entity(model)
        return None

    def get_all_for_project(self, project_id: str, limit: int = 50, offset: int = 0) -> List[TaskEntity]:
        models = self.db.query(Task).filter(Task.project_id == project_id).offset(offset).limit(limit).all()
        return [self._to_entity(t) for t in models]

    def create(self, task: TaskEntity) -> TaskEntity:
        model = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            due_date=task.due_date,
            priority=task.priority,
            list_id=task.list_id,
            project_id=task.project_id,
            creator_id=task.creator_id,
            created_at=task.created_at
        )
        self.db.add(model)
        
        for asn in task.assignees:
            asn_model = TaskAssignee(id=asn.id, task_id=asn.task_id, user_id=asn.user_id)
            self.db.add(asn_model)
            
        for cmt in task.comments:
            cmt_model = TaskComment(
                id=cmt.id,
                task_id=cmt.task_id,
                user_id=cmt.user_id,
                content=cmt.content,
                media_url=cmt.media_url,
                media_type=cmt.media_type,
                created_at=cmt.created_at
            )
            self.db.add(cmt_model)

        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, task: TaskEntity) -> TaskEntity:
        model = self.db.query(Task).filter(Task.id == task.id).first()
        if model:
            model.title = task.title
            model.description = task.description
            model.status = task.status
            model.due_date = task.due_date
            model.priority = task.priority
            model.list_id = task.list_id
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        return task

    def delete(self, task_id: str) -> None:
        self.db.query(Task).filter(Task.id == task_id).delete()
        self.db.commit()
