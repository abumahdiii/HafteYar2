from abc import ABC, abstractmethod

class IBotGateway(ABC):
    @abstractmethod
    def send_message(self, user_id: str, text: str) -> bool:
        """Sends a text message to a user via the bot platform."""
        pass
