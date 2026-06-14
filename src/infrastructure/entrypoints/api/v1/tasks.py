from fastapi import APIRouter, Depends
from typing import List
from src.infrastructure.entrypoints.schemas.task_schemas import TaskCreateRequest, TaskUpdateStatusRequest, TaskResponse
from src.application.use_cases.task_management import TaskManagementUseCase
from src.infrastructure.entrypoints.dependencies import get_task_use_case, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskResponse)
def create_task(
    request: TaskCreateRequest,
    current_user_id: str = Depends(get_current_user),
    use_case: TaskManagementUseCase = Depends(get_task_use_case)
):
    task = use_case.create_task(
        title=request.title,
        list_id=request.list_id,
        project_id=request.project_id,
        creator_id=current_user_id,
        description=request.description,
        priority=request.priority
    )
    return task

@router.get("/project/{project_id}", response_model=List[TaskResponse])
def get_tasks(
    project_id: str,
    current_user_id: str = Depends(get_current_user),
    use_case: TaskManagementUseCase = Depends(get_task_use_case)
):
    return use_case.get_tasks_for_project(project_id=project_id)

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: str,
    request: TaskUpdateStatusRequest,
    current_user_id: str = Depends(get_current_user),
    use_case: TaskManagementUseCase = Depends(get_task_use_case)
):
    return use_case.update_task_status(task_id=task_id, new_status=request.status)
