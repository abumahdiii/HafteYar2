from typing import Optional, List
from src.domain.entities.weekly_planning import WeeklyGoal, WeeklyReport
from src.domain.utils.ids import generate_id

class WeeklyPlanningUseCase:
    """
    Minimal skeleton for Weekly Planning.
    Execution is deferred to a future phase.
    """
    def __init__(self, db_session):
        self.db = db_session
        
    def generate_weekly_report(self, team_id: str) -> WeeklyReport:
        # Placeholder for AI-driven report generation logic
        raise NotImplementedError("Weekly Planning execution is deferred")

    def create_weekly_goal(self, team_id: str, title: str, description: Optional[str] = None) -> WeeklyGoal:
        # Placeholder for Goal creation
        raise NotImplementedError("Weekly Planning execution is deferred")
