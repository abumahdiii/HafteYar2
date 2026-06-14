import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Force environment API Key
os.environ["GEMINI_API_KEY"] = "dummy_key"
os.environ["TELEGRAM_BOT_TOKEN"] = "dummy_token"

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.infrastructure.database.session import Base
from src.infrastructure.database.models.user import User, UserAccount
from src.infrastructure.database.models.team import Team, TeamMember
from src.infrastructure.database.models.ai import Conversation, ExecutionPlan, ExecutionPlanItem
from src.infrastructure.database.models.bot import TelegramUserSession

from src.main import app
from fastapi.testclient import TestClient
from src.infrastructure.entrypoints.dependencies import get_db, get_ai_middleware, get_unified_input_gateway
from src.application.ai.middleware import AIMiddleware
from src.infrastructure.gateways.unified_input import UnifiedInputGateway
from src.application.ai.llm_provider import GeminiProvider

class TestTelegramHybridSubscription(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            'sqlite:///:memory:', 
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)
        
        cls.db = cls.SessionLocal()
        cls.real_provider = GeminiProvider(api_key=os.environ["GEMINI_API_KEY"])
        
        def override_get_db():
            yield cls.db
                
        def override_get_ai_middleware():
            return AIMiddleware(db_session=cls.db, llm_provider=cls.real_provider)

        def override_get_unified_input_gateway():
            return UnifiedInputGateway(ai_middleware=override_get_ai_middleware())

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ai_middleware] = override_get_ai_middleware
        app.dependency_overrides[get_unified_input_gateway] = override_get_unified_input_gateway

        cls.client = TestClient(app)

    def test_flow(self):
        # We will mock TelegramAdapter.send_message to capture the outgoing messages
        captured_payloads = []
        
        def mock_send_message(self_adapter, chat_id, text, reply_markup=None):
            captured_payloads.append({
                "text": text,
                "reply_markup": reply_markup
            })
            
        with patch('src.infrastructure.entrypoints.bot.telegram_bot.TelegramAdapter.send_message', new=mock_send_message):
            # 1. Test /start
            payload1 = {
                "update_id": 1,
                "message": {"chat": {"id": 111}, "text": "/start", "from": {"username": "user1"}}
            }
            res = self.client.post("/api/v1/bot/telegram/webhook", json=payload1)
            self.assertEqual(res.status_code, 200)
            
            # Wait for background task... test client executes background tasks immediately in older Starlette, 
            # but in newer versions we might need to manually run them or mock. 
            # Actually TestClient runs them synchronously if raised? Let's check captured_payloads.
            # Starlette TestClient runs background tasks after response.
            
            self.assertEqual(len(captured_payloads), 1)
            msg1 = captured_payloads[0]
            self.assertIn("سیستم مدیریت تیم هفته‌یار", msg1["text"])
            self.assertIn("reply_markup", msg1)
            self.assertTrue(any("تیم" in str(btn) for row in msg1["reply_markup"]["keyboard"] for btn in row))
            
            # 2. Test free text as Normal User (Should Upsell)
            payload2 = {
                "update_id": 2,
                "message": {"chat": {"id": 111}, "text": "ایجاد یک پروژه جدید", "from": {"username": "user1"}}
            }
            captured_payloads.clear()
            self.client.post("/api/v1/bot/telegram/webhook", json=payload2)
            self.assertEqual(len(captured_payloads), 2)
            # Actually, background task sends the upsell later. The webhook itself doesn't wait. 
            # Wait, `receive_message_handler` sends "در حال پردازش..." FIRST for free text.
            # So captured_payloads will have 2 items.
            self.assertEqual(len(captured_payloads), 2)
            self.assertIn("در حال پردازش", captured_payloads[0]["text"])
            self.assertIn("نیازمند لایسنس دستیار هوشمند", captured_payloads[1]["text"])
            
            # 3. Upgrade to Pro user
            # Find user
            account = self.db.query(UserAccount).filter_by(provider="telegram", provider_id="111").first()
            user = account.user
            
            # Create a team and team member with AI access
            team = Team(name="Pro Team")
            self.db.add(team)
            self.db.flush() # Ensure team.id is generated
            
            tm = TeamMember(team_id=team.id, user_id=user.id, has_ai_access=True)
            self.db.add(tm)
            
            # Update conversation active team
            conv = self.db.query(Conversation).filter_by(user_id=user.id).first()
            conv.active_team_id = team.id
            self.db.commit()
            
            # 4. Test free text as Pro User
            payload3 = {
                "update_id": 3,
                "message": {"chat": {"id": 111}, "text": "🤖 دستیار هوشمند (Pro)", "from": {"username": "user1"}}
            }
            captured_payloads.clear()
            self.client.post("/api/v1/bot/telegram/webhook", json=payload3)
            self.assertEqual(len(captured_payloads), 2)
            self.assertIn("دسترسی Pro دارید", captured_payloads[-1]["text"])

if __name__ == "__main__":
    unittest.main()
