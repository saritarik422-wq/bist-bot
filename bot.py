import os
import requests
from datetime import datetime
import pandas as pd
import yfinance as yf

# Telegram Bot Ayarları
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    """BİST ve dış akış istihbarat raporunu Telegram'a iletir."""
    if not TOKEN or not CHAT_ID:
        print("Uyarı: Telegram Token veya Chat ID tanımlı değil!")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Galaktik İstihbarat Raporu başarıyla iletildi komutan!")
    except Exception as e:
        print(f"Telegram mesajı gönderilirken hata oluştu: {e}")

def get_live_macd_and_rsi(ticker_symbol):
    """
    Yahoo Finance üzerinden BİST verisini çekip 12/26/9 MACD, 14 RSI ve Günlük Değişimi hesaplar.
    """
    try:
        df = yf.download(ticker_symbol, period="3m", interval="1d", progress=False)
        if df.empty or len(df) < 15:
            return "Veri Yetersiz", "Nötr", "0.00 TL", 0.0
        
        # Son kapanış ve bir önceki kapanış
        last_price = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        daily_change = ((last_price - prev_close) / prev_close) * 100
        
        # EMA & MACD Hesaplama (12, 26, 9)
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        last_macd = float(macd.iloc[-1])
        last_signal = float(signal.iloc[-1])
        prev_macd = float(macd.iloc[-2])
        prev_signal = float(signal.iloc[-2])
        
        # MACD Sinyal Mantığı
        if prev_macd < prev_signal and last_macd > last_signal:
            macd_status = "🚀 GÜÇLÜ AL (Kesişim)"
        elif last_macd > last_signal:
            macd_status = "🟢 AL (Pozitif)"
        elif prev_macd > prev_signal and last_macd < last_signal:
            macd_status = "⚠️ SAT (Aşağı Kesişim)"
        else:
            macd_status = "🔴 SAT / NÖTR"

        # RSI Hesaplama (14 Günlük)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        last_rsi = round(float(rsi.iloc[-1]), 1)

        return f"{last_price:.2f} TL", last_rsi, macd_status, daily_change
    except Exception as e:
        print(f"{ticker_symbol} hatası: {e}")
        return "Nötr", "Nötr", "0.00 TL", 0.0

def format_trade_signals(hisse_adi, fiyat_str, degisim, macd, rsi):
    """
    Canlı fiyata göre otomatik Alım, Stop ve Hedef seviyelerini hesaplar.
    """
    try:
        fiyat = float(fiyat_str.replace(" TL", "").replace(",", "."))
        stop_fiyati = fiyat * 0.965  # %3.5 Stop-Loss
        hedef_fiyat = fiyat * 1.080  # %8.0 Kâr Al
        yon = "🔺" if degisim >= 0 else "🔻"
        
        # Sadece fırsat veren veya kırılım yapan hisselerde net seviye basar
        if "GÜÇLÜ AL" in macd or degisim >= 3.5:
            return (
                f"🚨 *{hisse_adi}* - {fiyat:.2f} TL ({yon} %{degisim:.2f})\n"
                f"   ┣ 📥 *Alım Bölgesi:* {fiyat:.2f} TL\n"
                f"   ┣ 🛑 *Stop-Loss (%3.5):* {stop_fiyati:.2f} TL\n"
                f"   ┣ 💰 *Kâr Al Target (%8):* {hedef_fiyat:.2f} TL\n"
                f"   ┗ 📊 RSI: {rsi} | MACD: {macd}\n"
            )
        else:
            return (
                f"• *{hisse_adi}* - {fiyat:.2f} TL ({yon} %{degisim:.2f})\n"
                f"   ┗ RSI: {rsi} | MACD: {macd}\n"
            )
    except Exception:
        return f"• *{hisse_adi}* - {fiyat_str}\n"

def generate_pure_bist_battle_report():
    try:
        tarih = datetime.now().strftime("%d.%m.%Y")
        
        # 1. ÇEKİRDEK LİDERLER (SABİT DEVLER)
        lider_hisseler = [
            {"kod": "THYAO.IS", "ad": "THYAO"},
            {"kod": "ASELS.IS", "ad": "ASELS"},
            {"kod": "KCHOL.IS", "ad": "KCHOL"},
            {"kod": "TUPRS.IS", "ad": "TUPRS"},
            {"kod": "BIMAS.IS", "ad": "BIMAS"}
        ]
        
        # 2. DİNAMİK AL-SAT / HALKA ARZ VE FIRSAT RADARI
        firsat_havuzu = [
            {"kod": "GLRMK.IS", "ad": "GLRMK"},
            {"kod": "EFORC.IS", "ad": "EFORC"},
            {"kod": "LILAK.IS", "ad": "LILAK"},
            {"kod": "KOTON.IS", "ad": "KOTON"},
            {"kod": "ENTRA.IS", "ad": "ENTRA"}
        ]

        rapor = f"""
📈🎯 *GALAKTİK BİST NOKTA VURUŞ İSTİHBARATI*
📅 *Tarih:* {tarih}
—
🟢 *SİSTEM:* CANLI ALIM, STOP-LOSS VE KÂR AL SEVİYELERİ AKTİF!

⭐ *ÇEKİRDEK LİDER HİSSELER:*
"""
        for h in lider_hisseler:
            fiyat, rsi, macd, degisim = get_live_macd_and_rsi(h["kod"])
            rapor += format_trade_signals(h["ad"], fiyat, degisim, macd, rsi)

        rapor += "\n🔥 *YENİ HALKA ARZ & NOKTA ATIŞI AL-SAT RADARI:* \n"
        for h in firsat_havuzu:
            fiyat, rsi, macd, degisim = get_live_macd_and_rsi(h["kod"])
            rapor += format_trade_signals(h["ad"], fiyat, degisim, macd, rsi)

        rapor += """
🚀 *SİSTEM DURUMU:*
• Tüm Seviyeler Canlı Fiyat Üzerinden Otomatik Hesaplandı
• %3.5 Stop-Loss & %8.0 Kâr Al Disiplini Aktif
"""
        return rapor.strip()
    except Exception as e:
        return f"⚠️ Rapor Hatası: {e}"

if __name__ == "__main__":
    bulten = generate_pure_bist_battle_report()
    send_telegram_message(bulten)
