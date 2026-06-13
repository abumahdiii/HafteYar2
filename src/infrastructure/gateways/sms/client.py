import httpx
from src.application.interfaces.sms_gateway import ISmsGateway
from src.infrastructure.config.settings import settings

class KavenegarSmsGateway(ISmsGateway):
    def send_otp(self, phone: str, code: str) -> bool:
        if settings.SMS_PROVIDER == "console":
            print(f"--- CONSOLE SMS --- To: {phone} | Code: {code}")
            return True
            
        url = f"https://api.kavenegar.com/v1/{settings.SMS_API_KEY}/verify/lookup.json"
        params = {
            "receptor": phone,
            "token": code,
            "template": settings.SMS_TEMPLATE
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Error sending SMS via Kavenegar: {e}")
            return False
