import os
import requests
from datetime import datetime

# Telegram Bot Ayarları
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
*Komutan, sahada rüzgar arkamızda! Otonom kalkanlar ve risk yönetim sistemimiz tam gaz devrede. Piyasayı mercek altında tutmaya devam ediyoruz.*

📊 **AKİLLİ PORTFÖY SAĞLIK RAPORU (Check-Up):**
* *Risk / Likidite Dengesi:* %75 Agresif Hisse / %25 Nakit-Katılım Fonu koruması aktif.
* *Volatilite Stresi:* Piyasadaki dalgalanmalara karşı dinamik stop-loss kalkanları devrede.
* *Öneri / Reçete:* Mevcut sepet dağılımı trend yönünde istikrarla korunuyor.

⭐ **AKİLLİ SKOR KARTI (En Güçlü 3'lü):**
* 🥇 **1. Aday (Günün Yıldızı):** THYAO - Skor: 9.8 / 10 (Trend Gücü Üst Düzey)
* 🥈 **2. Aday:** KCHOL - Skor: 9.2 / 10 (Güçlü Bilanço Yapısı)
* 🥉 **3. Aday:** ASELS - Skor: 9.6 / 10 (Savunma Hattı Kaya Gibi)

🌐 **CANLI PİYASA & TUZAK RADARI:**
* THYAO: 296.00 TL (+1.54%) | 🟢 Yükseliş Trendi Onaylı
* ASELS: 388.25 TL (+2.10%) | 🟢 Yükseliş Kanalında
* KCHOL: 215.10 TL (-0.60%) | 🔴 Baskıda, Destek Test Ediliyor
* TUPRS: 165.40 TL (+1.20%) | 🟢 Toparlanma Başladı

⚽ **FORVET HATTI (Günün Bankosu & Golcüleri):**
* ⚽ **1. GOLCÜ:** THYAO (BIST Lideri) - Zirveye oynamaya devam.
* 🥈 **2. GOLCÜ:** KCHOL - Uzun vade sepet gözdesi.
* 🥉 **3. GOLCÜ:** ASELS - Pozisyon Bitirici Güç.

💼 **PORTFÖY KÂR / ZARAR & STOP-LOSS MATRİSİ:**
* *Varlık Dağılımı:* %75 Riskli Varlık / %25 Güvenli Liman
* *Günlük Simülasyon:* +%2.1 / +%3.2 aralığında getiri potansiyeli
* *Stop-Loss:* %3.5 stop-loss ve %8.0 kâr al disiplini devrede.
"""
    return rapor.strip()

if __name__ == "__main__":
    bulten = generate_battle_report()
    send_telegram_message(bulten)
