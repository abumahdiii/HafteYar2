from abc import ABC, abstractmethod
from typing import Any

class BaseBotAdapter(ABC):
    """
    Base interface for external messaging bots (Telegram, Bale, etc.)
    Bot layers act ONLY as I/O adapters and must not contain any business or AI logic.
    """
    
    @abstractmethod
    def send_message(self, chat_id: str, text: str) -> None:
        """Sends a message back to the user via the external messaging platform."""
        pass

    @abstractmethod
    def receive_message_handler(self, payload: dict) -> None:
        """Parses the incoming payload and translates it to internal domain requests."""
        pass

    @abstractmethod
    def format_response(self, plan_or_status: Any) -> str:
        """Formats the internal business logic responses into user-friendly messages."""
        pass
