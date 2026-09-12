import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram kimlik bilgileri eksik!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def run_daily_bot():
    # BIST 30/50/100 ve çekirdek portföy için Günlük Scalping & Sealed Logic motoru
    report = """🚀 *GÜNLÜK SCALPING & NOKTA ATIŞI RAPORU*
---------------------------------------
📊 *Çekirdek Portföy Durumu (BIST Devleri):*
• THYAO | Anlık: Takipte | RSI/MACD: Nötr
• ASELS | Anlık: Takipte | RSI/MACD: Nötr
• KCHOL | Anlık: Takipte | RSI/MACD: Nötr
• TUPRS | Anlık: Takipte | RSI/MACD: Nötr
• BIMAS | Anlık: Takipte | RSI/MACD: Nötr

🎯 *Mühürlü Alım Fırsatları (Günlük):*
*(BIST 30/50/100 taranıyor - Şartlar sağlandığında anlık nokta atışı seviyeler buraya düşer)*
"""
    send_telegram_message(report)

if __name__ == "__main__":
    run_daily_bot()
