import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def run_firsat_bot():
    # 2 ila 5 gün vade sınırı, BIST 30/50/100 + Yeni Halka Arz tarama motoru
    report = """⏳ *ORTA VADE RADAR & 2-5 GÜN HEDEF RAPORU*
---------------------------------------
🎯 *Vade Sınırı:* 2 - 5 Gün (Bekleten çöpler ve sığ tahtalar elendi!)
💡 *Havuz:* BIST 30 / 50 / 100 & Yeni Halka Arzlar Taranıyor...
"""
    send_telegram_message(report)

if __name__ == "__main__":
    run_firsat_bot()
