import os
import requests

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_alert(message):
    """ส่งแจ้งเตือนเข้า Discord Webhook"""
    if not DISCORD_WEBHOOK:
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=5)
    except Exception as e:
        print(f"⚠️ Discord alert error: {e}")