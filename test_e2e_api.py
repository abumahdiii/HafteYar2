import sys
import os
import json
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.abspath("."))

from src.main import app
from src.infrastructure.entrypoints.dependencies import get_current_user
from src.infrastructure.database.session import SessionLocal, engine, Base
from src.infrastructure.database.models.ai import Conversation
from src.application.ai.middleware import AIMiddleware
from src.domain.utils.ids import generate_id

# 1. Setup Database
Base.metadata.create_all(bind=engine)
db = SessionLocal()

# 2. Mock Dependency
def override_get_current_user():
    return "usr_test123"

app.dependency_overrides[get_current_user] = override_get_current_user

# 3. Setup a mock conversation
conv_id = generate_id("cnv")
conv = Conversation(
    id=conv_id,
    user_id="usr_test123",
    active_team_id="tem_W7qTsrFLb4J6Ap6dZH38SP1n"
)
db.add(conv)
db.commit()

# 4. Monkeypatch OpenAI client for AI Middleware
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

# We need to monkeypatch the openai client inside AIMiddleware.
# It is instantiated per AIMiddleware instance.
# We will monkeypatch the globally used module or just intercept the process_user_input call.
import src.application.ai.middleware
original_init = src.application.ai.middleware.AIMiddleware.__init__
def new_init(self, db_session):
    original_init(self, db_session)
    self.client.chat.completions.create = mock_create
src.application.ai.middleware.AIMiddleware.__init__ = new_init

# 5. Run E2E Test
client = TestClient(app)

payload = {
    "conversation_id": conv_id,
    "prompt": "برای پروژه Haftyar Mobile App سه تسک طراحی UI، پیادهسازی Flutter و تست نهایی ایجاد کن."
}

print("=== Sending Request ===")
print(json.dumps(payload, indent=2, ensure_ascii=False))

response = client.post("/api/v1/ai/plan", json=payload)

print("\n=== Response Status ===")
print(response.status_code)

print("\n=== Response Payload ===")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

db.close()
