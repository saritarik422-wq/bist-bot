import os
import requests
from datetime import datetime

# Telegram Bot Ayarları
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    """Raporu Telegram'a gönderir ve hataları açıkça gösterir."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    print(f"Telegram Sunucu Yanıt Kodu: {response.status_code}")
    print(f"Telegram Sunucu Yanıt Metni: {response.text}")
    
    # Hata varsa GitHub Actions'ı kırmızı yap ve durdur
    response.raise_for_status()
    print("Savaş raporu başarıyla cep telefonuna iletildi komutan!")

def generate_battle_report():
    """Nihai Savaş Odası Raporunu Oluşturur"""
    tarih = datetime.now().strftime("%d.%m.%Y")
    
    rapor = f"""
🏆 **ŞAMPİYONLAR LİGİ NİHAİ SAVAŞ ODASI**
📅 *Tarih: {tarih}*
—
🔥 **TEKNİK DİREKTÖRÜN SOYUNMA ODASI KONUŞMASI:**
*Komutan, hatayı yakalamak için sistem loglarını inceliyoruz!*
"""
    return rapor.strip()

if __name__ == "__main__":
    bulten = generate_battle_report()
    send_telegram_message(bulten)
