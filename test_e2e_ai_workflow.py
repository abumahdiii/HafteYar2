import sys
import os
import json
from fastapi.testclient import TestClient

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from src.main import app
from src.infrastructure.entrypoints.dependencies import get_current_user
from src.infrastructure.database.session import SessionLocal, engine, Base
from src.infrastructure.database.models.ai import Conversation, ExecutionPlan
from src.infrastructure.database.models.team import Team
from src.infrastructure.database.models.project import Project
from src.domain.utils.ids import generate_id
import src.application.ai.middleware
from src.application.ai.tool_registry import registry

# 1. Setup DB
Base.metadata.create_all(bind=engine)
db = SessionLocal()

def override_get_current_user():
    return "usr_test_e2e"

app.dependency_overrides[get_current_user] = override_get_current_user

team_id = "tem_test_e2e_1"
existing_team = db.query(Team).filter(Team.id == team_id).first()
if not existing_team:
    team = Team(id=team_id, name="Test Team", is_active=True)
    db.add(team)
    db.commit()

conv_id = generate_id("cnv")
conv = Conversation(
    id=conv_id,
    user_id="usr_test_e2e",
    active_team_id=team_id
)
db.add(conv)
db.commit()

# 2. Mock Handlers for Registry
def mock_create_project(db_session, context, params):
    from src.domain.utils.ids import generate_id
    # We mock returning an object with an ID
    class MockEntity:
        def __init__(self, id):
            self.id = id
    # Pretend we created it
    return MockEntity(generate_id("prj"))

def mock_create_task(db_session, context, params):
    # Verify project_id is present and resolved
    assert "project_id" in params, "project_id missing"
    assert params["project_id"].startswith("prj_"), f"project_id not resolved: {params['project_id']}"
    return True

registry.register("CreateProject", mock_create_project)
registry.register("CreateTask", mock_create_task)

# 3. Mock Provider inside AIMiddleware
class MockProvider:
    def generate_plan(self, system_prompt, user_input):
        return """[
        {"tool_name": "CreateProject", "parameters": {"name": "Haftyar Mobile App", "project_reference_id": "ref_mobile_app"}},
        {"tool_name": "CreateTask", "parameters": {"title": "طراحی UI", "project_id": "${ref_mobile_app.id}"}}
    ]"""

    def refine_parameters(self, original_parameters, feedback):
        return '{"title": "طراحی UI پیشرفته", "project_id": "${ref_mobile_app.id}"}'

original_init = src.application.ai.middleware.AIMiddleware.__init__
def new_init(self, db_session, llm_provider=None):
    original_init(self, db_session, llm_provider)
    self.provider = MockProvider()
src.application.ai.middleware.AIMiddleware.__init__ = new_init


client = TestClient(app)

print("=== 1. Generate Plan ===")
plan_res = client.post("/api/v1/ai/plan", json={"conversation_id": conv_id, "prompt": "build UI"})
plan_data = plan_res.json()
plan_id = plan_data["id"]
items = plan_data["items"]
print(f"Generated Plan: {plan_id} with {len(items)} items.")

item_task = next(i for i in items if i["tool_name"] == "CreateTask")

print("\n=== 2. Review Plan (Mark Task as YELLOW) ===")
review_payload = {
    "reviews": [
        {"item_id": item_task["id"], "final_state": "YELLOW", "feedback_text": "Make it advanced UI"}
    ]
}
client.patch(f"/api/v1/ai/plan/{plan_id}/review", json=review_payload)
plan_get = client.get(f"/api/v1/ai/plan/{plan_id}").json()
yellow_item = next(i for i in plan_get["items"] if i["id"] == item_task["id"])
print(f"Item State after review: {yellow_item['final_state']}")

print("\n=== 3. Try to Execute Plan (Should Fail due to YELLOW) ===")
exec_fail = client.post(f"/api/v1/ai/plan/{plan_id}/execute")
print(f"Execute Result Status Code: {exec_fail.status_code}")
print(f"Execute Error: {exec_fail.json()}")

print("\n=== 4. Refine Plan ===")
# We resend the reviews payload which contains the feedback
refine_res = client.post(f"/api/v1/ai/plan/{plan_id}/refine", json=review_payload)
print(f"Refinement Result: {refine_res.json()}")

plan_get_refined = client.get(f"/api/v1/ai/plan/{plan_id}").json()
refined_item = next(i for i in plan_get_refined["items"] if i["id"] == item_task["id"])
print(f"Refined Item State: {refined_item['final_state']}")
print(f"Refined Item Version: {refined_item['current_version_index']}")
print(f"Refined Item Parameters: {refined_item['parameters']}")

print("\n=== 5. Execute Plan (Should Succeed now) ===")
exec_success = client.post(f"/api/v1/ai/plan/{plan_id}/execute")
print(f"Execute Output: {exec_success.json()}")

db.close()
