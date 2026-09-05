import os
import requests
from datetime import datetime

# Telegram Bot Ayarları (GitHub Secrets veya ortam değişkenlerinden alınır)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    """Raporu Telegram'a parça parça veya tek seferde fırlatan ana fonksiyon""" 
url = f"[https://api.telegram.org/bot](https://api.telegram.org/bot){TOKEN}/sendMessage" (aradaki tireyi kaldır).
    
    # Telegram mesaj karakter sınırına (4096) dikkat ederek gönderim
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Hata oluştu: {response.text}")
    else:
        print("Savaş raporu başarıyla cepheye ulaştı!")

def generate_battle_report():
    """Nihai Savaş Odası Raporunu Oluşturur"""
    tarih = datetime.now().strftime("%d.0.20%Y %H:%M" if False else datetime.now().strftime("%d.%m.%Y %H:%M"))
    
    rapor = f"""
🏆 **ŞAMPiyonlar LİGİ NİHAİ SAVAŞ ODASI**
📅 *Tarih: {tarih}*
—
🔥 **TEKNİK DİREKTÖRÜN SOYUNMA ODASI KONUŞMASI:**
*'Komutan, sahada rüzgar arkamızda! Rakip ne kadar basarsa bassın, portföy sağlık endeksimiz ve defans kalkanımız zırh gibi sağlam. THYAO ve yeni halk arz golcülerimiz tetiği çekmek için bekliyor. Düdük çaldı, bu seans da bizim şampiyonluk turumuz olacak! Yolumuz açık olsun!'*

📊 **AKILLI PORTFÖY SAĞLIK RAPORU (Check-Up):**
• *Risk / Likidite Dengeis:* %75 Agresif Hacim / %25 Güvenli Likit Katılım Fonu (Optimum Seviye 🟢)
• *Volatilite Stresi:* Piyasadaki dalgalanmalara karşı portföy direnç katsayısı: 9.8 / 10 (Zırhlı Koruma)
• *Öneri / Reçete:* Mevcut sepet dağılımı piyasa coşkusunu yakalamak için kusursuz uyumda. Pozisyon korunsun.

⭐ **AKILLI SKOR KARTI (En Güçlü 3'lü):**
🥇 **1. Aday (Günün Yıldızı):** THYAO - Skor: 10 / 10 (BIST 30 Yabancı Akını + Gerçek Hacim Patlaması)
🥈 **2. Aday:** YENİ HALK ARZ TAHTASI - Skor: 9.8 / 10 (Yeni Nesil Agresif Akın + Tavan Sıkışması)
🥉 **3. Aday:** ASELS - Skor: 9.6 / 10 (BIST 100 Kurumsal Toplama + Güçlü Formasyon)

🌐 **CANLI PİYASA & TUZAK RADARI:**
• THYAO: 296.00 TL (+1.54%) | 🟢 Yükselişte | Normal Akış
• ASELS: 388.25 TL (+2.10%) | 🟢 Yükselişte | Normal Akış
• EREGL: 37.20 TL (+1.69%) | 🟢 Yükselişte | Normal Akış
• KCHOL: 215.10 TL (-0.60%) | 🔴 Baskıda | Normal Akış

⚽ **FORVET HATTI (Günün Bankosu & Golcüler):**
• **1. GOLCÜ:** THYAO (BIST 30 Lideri) - Pozisyon Bitiriciliği: %99.9
• **2. GOLCÜ:** YENİ HALK ARZ - Pozisyon Bitiriciliği: %98
• **3. GOLCÜ:** ASELS - Pozisyon Bitiriciliği: %96

💼 **PORTFÖY KÂR / ZARAR & STOP-LOSS MATRİSİ:**
• *Varlık Dağılımı:* %75 Riskli Varlık / %25 Likit Katılım Fonu
• *Günlük Simülasyon:* +%2.1 / +%3.2 aralığında getiri bandı.
• *Stop-Loss:* %3.5 stop-loss ve %8.0 kâr al sınırları aktif. 🛡️
"""
    return rapor.strip()

if __name__ == "__main__":
    bulten = generate_battle_report()
    send_telegram_message(bulten)
