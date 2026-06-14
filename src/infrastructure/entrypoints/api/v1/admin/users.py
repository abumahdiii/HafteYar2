from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from src.infrastructure.database.session import get_db
from src.infrastructure.entrypoints.dependencies import get_current_admin
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.infrastructure.entrypoints.schemas.user_schemas import UserListResponse, UserResponse, UserCreateRequest, UserUpdateRequest
from src.domain.entities.user import UserEntity
from src.domain.utils.ids import new_user_id

router = APIRouter(prefix="/users", tags=["admin_users"])

@router.get("", response_model=UserListResponse)
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    users = repo.get_all(skip=skip, limit=limit)
    total = repo.count()
    return UserListResponse(
        items=[UserResponse(
            id=u.id, username=u.username, email=u.email, phone=u.phone,
            is_admin=u.is_admin, created_at=u.created_at, accounts=[]
        ) for u in users],
        total=total
    )

@router.post("", response_model=UserResponse)
def create_user(
    request: UserCreateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    if request.username and repo.get_by_username(request.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if request.phone and repo.get_by_phone(request.phone):
        raise HTTPException(status_code=400, detail="Phone already exists")

    from src.domain.utils.security import get_password_hash
    from datetime import datetime

    new_user = UserEntity(
        id=new_user_id(),
        username=request.username,
        email=request.email,
        phone=request.phone,
        password_hash=get_password_hash(request.password) if request.password else None,
        is_admin=request.is_admin,
        created_at=datetime.utcnow(),
        accounts=[]
    )
    created = repo.create(new_user)
    return UserResponse(
        id=created.id, username=created.username, email=created.email, phone=created.phone,
        is_admin=created.is_admin, created_at=created.created_at, accounts=[]
    )

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    request: UserUpdateRequest,
    admin_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Manual update for now since UserEntity isn't fully immutable but repo needs a method
    # Let's add update to repo or just use db session
    from src.infrastructure.database.models.user import User
    from src.domain.utils.security import get_password_hash
    
    user_model = db.query(User).filter(User.id == user_id).first()
    if request.username is not None:
        user_model.username = request.username
    if request.email is not None:
        user_model.email = request.email
    if request.phone is not None:
        user_model.phone = request.phone
    if request.password is not None:
        user_model.password_hash = get_password_hash(request.password)
    if request.is_admin is not None:
        user_model.is_admin = request.is_admin
        
    db.commit()
    updated_user = repo.get_by_id(user_id)
    
    return UserResponse(
        id=updated_user.id, username=updated_user.username, email=updated_user.email, phone=updated_user.phone,
        is_admin=updated_user.is_admin, created_at=updated_user.created_at, accounts=[]
    )
