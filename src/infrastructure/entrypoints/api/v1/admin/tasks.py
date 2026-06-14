from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.models.task import Task
from src.infrastructure.entrypoints.schemas.task_schemas import TaskResponse, TaskListResponse

router = APIRouter(prefix="/tasks", tags=["admin_tasks"])

@router.get("", response_model=TaskListResponse)
def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in tasks],
        total=total
    )

@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
