from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class UserAccountEntity:
    id: str
    user_id: str
    provider: str
    provider_id: str

@dataclass
class UserEntity:
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    accounts: List[UserAccountEntity] = field(default_factory=list)
