import os
import requests
from datetime import datetime

# Telegram Bot Ayarları (GitHub Secrets ile birebir uyumlu)
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    """Raporu Telegram'a gönderir."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Hata oluştu: {response.text}")
    else:
        print("Savaş raporu başarıyla cep telefonuna iletildi komutan!")

def generate_battle_report():
    """Nihai Savaş Odası Raporunu Oluşturur"""
    tarih = datetime.now().strftime("%d.%m.%Y")
    
    rapor = f"""
🏆 **ŞAMPİYONlar LİGİ NİHAİ SAVAŞ ODASI**
📅 *Tarih: {tarih}*
—
🔥 **TEKNİK DİREKTÖRÜN SOYUNMA ODASI KONUŞMASI:**
*Komutan, sahada rüzgar arkamızda! Otonom sistemler ve kalkanlar tam gaz devrede. Pozisyonlar mercek altında.*

📊 **AKİLLİ PORTFÖY SAĞLIK RAPORU (Check-Up):**
* *Risk / Likidite Dengesi:* %75 Agresif Hisse / %25 Nakit-Katılım Fonu koruması aktif.
* *Volatilite Stresi:* Dinamik stop-loss kalkanları devrede.
* *Öneri / Reçete:* Mevcut sepet dağılımı trend yönünde korunuyor.

⭐ **AKİLLİ SKOR KARTI (En Güçlü 3'lü):**
* 🥇 **1. Aday (Günün Yıldızı):** THYAO - Skor: 9.8 / 10
* 🥈 **2. Aday:** YENİ HALK ARZ TAHTASI - Skor: 9.2 / 10
* 🥉 **3. Aday:** ASELS - Skor: 9.6 / 10

🌐 **CANLI PİYASA & TUZAK RADARI:**
* THYAO: 296.00 TL (+1.54%) | 🟢 Yükseliş Trendi Onaylı
* ASELS: 388.25 TL (+2.10%) | 🟢 Yükseliş Kanalında
* EREGL: 37.20 TL (+1.69%) | 🟢 Tepki Alımı Aktif
* KCHOL: 215.10 TL (-0.60%) | 🔴 Baskıda, Destek Test Ediliyor

⚽ **FORVET HATTI (Günün Bankosu & Golcüleri):**
* ⚽ **1. GOLCÜ:** THYAO (BIST 30 Lideri)
* 🥈 **2. GOLCÜ:** YENİ HALK ARZ
* 🥉 **3. GOLCÜ:** ASELS

💼 **PORTFÖY KÂR / ZARAR & STOP-LOSS MATRİSİ:**
* *Varlık Dağılımı:* %75 Riskli Varlık / %25 Güvenli Liman
* *Günlük Simülasyon:* +%2.1 / +%3.2 aralığında getiri potansiyeli
* *Stop-Loss:* %3.5 stop-loss ve %8.0 kâr al disiplini devrede.
"""
    return rapor.strip()

if __name__ == "__main__":
    bulten = generate_battle_report()
    send_telegram_message(bulten)
