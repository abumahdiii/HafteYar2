import sys
import os
import json
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
    team = Team(id=generate_id("tem"), name="تیم AI شتابدهنده ترشیز")
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
    
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Run middleware
    middleware = AIMiddleware(db_session=db)
    
    # Monkeypatch the gapgpt client call to return a mock JSON response
    class MockMessage:
        content = """[
            {"tool_name": "CreateProject", "parameters": {"name": "Haftyar Mobile App", "project_reference_id": "ref_mobile_app"}},
            {"tool_name": "CreateTask", "parameters": {"title": "طراحی UI", "project_id": "${ref_mobile_app.id}"}},
            {"tool_name": "CreateTask", "parameters": {"title": "پیاده‌سازی Flutter", "project_id": "${ref_mobile_app.id}"}},
            {"tool_name": "CreateTask", "parameters": {"title": "تست نهایی", "project_id": "${ref_mobile_app.id}"}}
        ]"""
    class MockChoice:
        message = MockMessage()
    class MockResponse:
        choices = [MockChoice()]
        
    def mock_create(*args, **kwargs):
        return MockResponse()
        
    middleware.client.chat.completions.create = mock_create
    
    prompt = """یک پروژه جدید به نام Haftyar Mobile App ایجاد کن و سپس سه تسک زیر را داخل همان پروژه بساز:
- طراحی UI
- پیادهسازی Flutter
- تست نهایی"""

    plan = middleware.process_user_input(conversation.id, prompt)
    
    # Output structured JSON dump
    output = {
        "execution_plan": {
            "id": plan.id,
            "status": plan.status,
            "context_snapshot": plan.context_snapshot,
            "items": []
        }
    }
    
    for item in plan.items:
        output["execution_plan"]["items"].append({
            "id": item.id,
            "tool_name": item.tool_name,
            "parameters": item.parameters,
            "initial_state": item.initial_state,
            "final_state": item.final_state,
            "current_version_index": item.current_version_index,
            "executed": item.executed
        })
        
    print(json.dumps(output, indent=4, ensure_ascii=False))
    
    db.close()

if __name__ == "__main__":
    test_middleware()
