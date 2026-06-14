import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.database.session import Base
from src.infrastructure.database.models.user import User
from src.infrastructure.database.models.team import Team
from src.infrastructure.database.models.ai import Conversation, ExecutionPlan
from src.application.ai.middleware import AIMiddleware
from src.domain.utils.ids import generate_id

def test_middleware():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Create user, team, conversation
    user = User(id=generate_id("usr"), phone="1234567890")
    team = Team(id=generate_id("tem"), name="Test Team", owner_id=user.id)
    db.add(user)
    db.add(team)
    db.commit()
    
    conversation = Conversation(
        id=generate_id("con"),
        user_id=user.id,
        channel="web",
        active_team_id=team.id
    )
    db.add(conversation)
    db.commit()
    
    # Run middleware
    middleware = AIMiddleware(db_session=db)
    
    # This will use the mock fallback since GAPGPT_API_KEY is fake
    plan = middleware.process_user_input(conversation.id, "Create a task for the UI design")
    
    print(f"Generated Plan ID: {plan.id}")
    print(f"Plan Status: {plan.status}")
    print(f"Context Snapshot: {plan.context_snapshot}")
    
    for item in plan.items:
        print(f"Item Tool: {item.tool_name}")
        print(f"Item Params: {item.parameters}")
        print(f"Item Initial State: {item.initial_state}")
        
    db.close()

if __name__ == "__main__":
    test_middleware()
