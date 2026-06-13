from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class ProjectListEntity:
    id: str
    project_id: str
    name: str
    position: int
    created_at: datetime

@dataclass
class ProjectEntity:
    id: str
    team_id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    lists: List[ProjectListEntity] = field(default_factory=list)
