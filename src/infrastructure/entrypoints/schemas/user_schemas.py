from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserAccountResponse(BaseModel):
    id: str
    provider: str
    provider_id: str

class UserResponse(BaseModel):
    id: str
    username: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_admin: bool
    created_at: datetime
    accounts: List[UserAccountResponse] = []

class UserCreateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_admin: bool = False

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
