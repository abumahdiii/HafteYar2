from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from src.infrastructure.entrypoints.dependencies import get_db, get_ai_middleware, get_unified_input_gateway
from src.application.ai.middleware import AIMiddleware
from src.infrastructure.entrypoints.bot.telegram_bot import TelegramAdapter
from src.infrastructure.gateways.unified_input import UnifiedInputGateway
import os

router = APIRouter(prefix="/bot", tags=["Bots"])

def get_telegram_adapter(
    gateway: UnifiedInputGateway = Depends(get_unified_input_gateway)
) -> TelegramAdapter:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "dummy_token")
    return TelegramAdapter(token=token, gateway=gateway)

@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    adapter: TelegramAdapter = Depends(get_telegram_adapter)
):
    """
    Webhook endpoint for Telegram Bot.
    Must be completely non-blocking to prevent Telegram timeout/retries.
    """
    payload = await request.json()
    
    # Schedule the processing in the background
    background_tasks.add_task(adapter.receive_message_handler, payload)
    
    return {"status": "ok"}
