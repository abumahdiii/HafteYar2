from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from src.domain.entities.enums import TeamRole

@dataclass
class TeamMemberEntity:
    id: str
    team_id: str
    user_id: str
    role: TeamRole
    has_ai_access: bool = False

@dataclass
class TeamEntity:
    id: str
    name: str
    created_at: datetime
    subscription_expiry: datetime
    is_active: bool
    members: List[TeamMemberEntity] = field(default_factory=list)

    @property
    def is_subscription_valid(self) -> bool:
        return datetime.utcnow() < self.subscription_expiry and self.is_active
