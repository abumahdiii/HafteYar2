from abc import ABC, abstractmethod

class ISmsGateway(ABC):
    @abstractmethod
    def send_otp(self, phone: str, code: str) -> bool:
        """Sends an OTP code via SMS."""
        pass
