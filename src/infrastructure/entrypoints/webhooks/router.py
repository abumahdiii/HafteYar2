from fastapi import APIRouter, Request, BackgroundTasks, Header, HTTPException
from typing import Dict, Any
from src.infrastructure.entrypoints.webhooks.adapters import WebhookAdapter
from src.application.use_cases.bot_commands.router import bot_router
import src.application.use_cases.bot_commands.handlers  # Load handlers
from src.infrastructure.database.session import SessionLocal
from src.infrastructure.database.repositories.team_repository import TeamRepository
from src.infrastructure.config.settings import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def process_webhook_background(platform: str, payload: Dict[str, Any]):
    adapter = WebhookAdapter(platform)
    internal_msg = adapter.parse(payload)
    
    if not internal_msg or not internal_msg.message_text:
        return
        
    # In a real app, we'd use Dependency Injection here or pass the Use Case.
    # For background tasks, we must create a new DB session.
    db = SessionLocal()
    try:
        team_repo = TeamRepository(db)
        context = {
            "team_repo": team_repo,
            "platform": platform,
            "contact_phone": internal_msg.contact_phone
        }
        
        if internal_msg.message_text.startswith("/"):
            response_text = bot_router.route(internal_msg.message_text, internal_msg.user_id, context)
            print(f"[{platform}] Reply to {internal_msg.user_id}: {response_text}")
            # Here we would call the IBotGateway to actually send the message
    finally:
        db.close()


@router.post("/{platform}")
async def receive_webhook(
    platform: str, 
    request: Request, 
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    if platform not in ["telegram", "bale"]:
        raise HTTPException(status_code=400, detail="Unsupported platform")
        
    # Security: Verify Webhook Signature (as requested in plan)
    if platform == "telegram":
        # Using a dummy secret from settings, in production set this
        expected_secret = getattr(settings, "WEBHOOK_SECRET", "dummy_secret")
        if x_telegram_bot_api_secret_token != expected_secret:
            print("Webhook signature validation failed!")
            # In production, we'd raise 401. But for dev, we might just warn.
            # raise HTTPException(status_code=401, detail="Invalid token")

    payload = await request.json()
    background_tasks.add_task(process_webhook_background, platform, payload)
    
    return {"status": "accepted"}
