from src.infrastructure.database.models.user import User, UserAccount
from src.infrastructure.database.models.team import Team, TeamMember
from src.infrastructure.database.models.project import Project, ProjectList
from src.infrastructure.database.models.task import Task, TaskAssignee, TaskComment
from src.infrastructure.database.models.otp import OtpVerification
from src.infrastructure.database.models.subscription import Feature, SubscriptionPlan, PlanFeature, Subscription
from src.infrastructure.database.models.ai import Conversation, ChatMessage, AIToolExecution, ExecutionPlan, ExecutionPlanItem

# This __init__.py ensures all models are imported when alembic imports Base
