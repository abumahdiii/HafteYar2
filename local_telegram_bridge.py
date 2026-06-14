import os
import time
import requests
import json
import threading
import uvicorn
from src.main import create_app

# The Telegram Bot Token provided by the user
TELEGRAM_TOKEN = "8628336336:AAEu16p2vOtR-SXKmRA0h1b6z8Eb1QFqz9I"
WEBHOOK_URL = "http://127.0.0.1:8000/api/v1/bot/telegram/webhook"

# Disable any existing webhook to ensure getUpdates works
requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")

def poll_telegram():
    print("\n[Bridge] Starting Telegram Polling Bridge...")
    print("[Bridge] You can now send messages to your bot on Telegram!")
    offset = None
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset

            resp = requests.get(url, params=params, timeout=35)
            if resp.status_code == 200:
                data = resp.json()
                for update in data.get("result", []):
                    # Update offset to acknowledge receipt
                    offset = update["update_id"] + 1
                    
                    print(f"\n[Bridge] Forwarding update {update['update_id']} to local webhook...")
                    # Forward to local webhook
                    post_resp = requests.post(WEBHOOK_URL, json=update)
                    if post_resp.status_code != 200:
                        print(f"[Bridge] Warning: Local webhook returned {post_resp.status_code}")
                        
        except Exception as e:
            print(f"[Bridge] Polling Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Ensure token is in environment for the adapter
    os.environ["TELEGRAM_BOT_TOKEN"] = TELEGRAM_TOKEN
    
    # Provide a dummy API key if not set so the middleware doesn't crash on init
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = "dummy_key_for_local_testing"
    
    # Init DB
    from src.infrastructure.database.session import engine, Base
    from src.infrastructure.database.models.user import User
    from src.infrastructure.database.models.team import Team
    from src.infrastructure.database.models.project import Project
    from src.infrastructure.database.models.task import Task
    from src.infrastructure.database.models.ai import Conversation, ExecutionPlan
    Base.metadata.create_all(engine)

    # Run the polling bridge in a background thread
    t = threading.Thread(target=poll_telegram, daemon=True)
    t.start()
    
    # Run the FastAPI server locally
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=8000)
