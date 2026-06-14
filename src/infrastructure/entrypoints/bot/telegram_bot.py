import os
import httpx
from typing import Any
from src.infrastructure.entrypoints.bot.base_bot import BaseBotAdapter
from src.infrastructure.gateways.unified_input import UnifiedInputGateway
from src.infrastructure.gateways.schemas import AIRequest, GatewayResponse
from src.infrastructure.database.models.ai import ExecutionPlan

class TelegramAdapter(BaseBotAdapter):
    def __init__(self, token: str, gateway: UnifiedInputGateway):
        self.token = token
        self.gateway = gateway
        self.api_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id: str, text: str, reply_markup: dict = None) -> None:
        """Synchronous HTTP call to Telegram API"""
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            payload["reply_markup"] = reply_markup
            
        try:
            with httpx.Client() as client:
                res = client.post(url, json=payload, timeout=10.0)
                if res.status_code != 200:
                    print(f"Telegram API Error: {res.text}")
        except Exception as e:
            print(f"Error sending message to Telegram: {e}")

    def format_response(self, plan_or_status: Any) -> str:
        """Formats ExecutionPlan or status to string"""
        if isinstance(plan_or_status, ExecutionPlan):
            return f"✅ پلان ایجاد شد.\nشناسه: `{plan_or_status.id}`\nتعداد تسک‌ها: {len(plan_or_status.items)}\nوضعیت: {plan_or_status.status}"
        return str(plan_or_status)

    def answer_callback_query(self, callback_query_id: str, text: str = None) -> None:
        """Answers a callback query to stop the loading circle on the user's side."""
        url = f"{self.api_url}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        try:
            with httpx.Client() as client:
                client.post(url, json=payload, timeout=5.0)
        except Exception as e:
            print(f"Error answering callback query: {e}")

    def receive_message_handler(self, payload: dict) -> None:
        """Main processing method that runs in background."""
        is_callback = False
        callback_id = None
        
        if "callback_query" in payload:
            cb = payload["callback_query"]
            message = cb.get("message", {})
            chat_id = str(message.get("chat", {}).get("id"))
            text = cb.get("data", "")
            username = cb.get("from", {}).get("username")
            is_callback = True
            callback_id = cb.get("id")
            
            # Immediately answer callback to stop loading circle
            self.answer_callback_query(callback_id)
            
        elif "message" in payload:
            message = payload["message"]
            chat_id = str(message.get("chat", {}).get("id"))
            text = message.get("text", "").strip()
            username = message.get("from", {}).get("username")
        else:
            return

        if not chat_id or not text:
            return

        print(f"[Telegram] Received from {chat_id}: {text} (Callback: {is_callback})")
        
        if not is_callback and text != "/start" and text != "/status" and not text.startswith("/execute"):
            self.send_message(chat_id, "در حال پردازش درخواست شما...")

        request = AIRequest(
            source="telegram",
            chat_id=chat_id,
            user_id=None,
            username=username,
            payload=text,
            is_callback=is_callback,
            callback_id=callback_id,
            metadata={"update_id": payload.get("update_id")}
        )

        try:
            response = self.gateway.route_request(request)
            
            if isinstance(response, GatewayResponse):
                reply_markup = None
                if response.inline_buttons:
                    keyboard = [[{"text": btn.text, "callback_data": btn.callback_data} for btn in row] for row in response.inline_buttons]
                    reply_markup = {"inline_keyboard": keyboard}
                elif response.buttons:
                    keyboard = [[{"text": btn} for btn in row] for row in response.buttons]
                    reply_markup = {
                        "keyboard": keyboard,
                        "resize_keyboard": True
                    }
                self.send_message(chat_id, response.text, reply_markup)
            else:
                formatted_response = self.format_response(response)
                self.send_message(chat_id, formatted_response)
            
        except Exception as e:
            print(f"Error processing message: {e}")
            self.send_message(chat_id, "متاسفانه خطایی رخ داد.")
