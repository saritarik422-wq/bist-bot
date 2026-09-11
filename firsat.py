from datetime import datetime, timezone, timedelta
import os
import pandas as pd
import requests
import yfinance as yf

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def telegram_mesaj_gonder(mesaj):
    """Telegram üzerinden anlık ve biçimlendirilmiş mesaj gönderir."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("HATA: Telegram Token veya Chat ID tanımlanmamış!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Yanıt Kodu: {response.status_code}")
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

# --- TARANACAK BIST HİSSELERİ ---
HISSOLER = [
    "GARAN.IS", "AKBNK.IS", "ISCTR.IS", "YKBNK.IS", "VAKBN.IS", "HALKB.IS",
    "THYAO.IS", "PGSUS.IS", "TUPRS.IS", "PETKM.IS", "KCHOL.IS", "SAHOL.IS",
    "ASELS.IS", "EREGL.IS", "KARDM.IS", "SISE.IS", "BIMAS.IS", "MGROS.IS",
    "TOASO.IS", "FROTO.IS", "ARCLK.IS", "ENKAI.IS", "EKGYO.IS", "SASA.IS",
    "HEKTS.IS", "ODAS.IS", "KOZAA.IS", "KOZAL.IS", "TCELL.IS", "TTKOM.IS"
]

def rsi_hesapla(df, period=7):
    """Verilen fiyat serisi için RSI hesaplar."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def piyasa_tara():
    """Hisseleri indirir, RSI-7 değerlerini hesaplar ve fırsatları yakalar."""
    print("BIST taraması başlatılıyor...")
    bulunan_firsatlar = []

    for hisse in HISSOLER:
        try:
            # Son günlerin verisini çek
            data = yf.download(hisse, period="1mo", interval="1d", progress=False)
            if data.empty or len(data) < 10:
                continue
            
            # Çoklu sütun yapısını düzelt
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data['RSI'] = rsi_hesapla(data, 7)
            son_rsi = data['RSI'].iloc[-1]
            son_fiyat = data['Close'].iloc[-1]

            print(f"{hisse} -> Son Fiyat: {son_fiyat:.2f}, RSI-7: {son_rsi:.2f}")

            # RSI 30 altı aşırı satım (fırsat) bölgesi
            if son_rsi < 30:
                stop_loss = son_fiyat * 0.965  # %3.5 stop loss
                target = son_fiyat * 1.08      # %8 hedef
                
                mesaj = (
                    f"🎯 *RSI-7 FIRSAT SİNYALİ!*\n"
                    f"▫️ *Hisse:* `{hisse}`\n"
                    f"▫️ *Fiyat:* `{son_fiyat:.2f} TL`\n"
                    f"▫️ *RSI-7:* `{son_rsi:.2f}` (Aşırı Satım)\n"
                    f"🛑 *Stop-Loss (%3.5):* `{stop_loss:.2f} TL`\n"
                    f"💰 *Kâr Al Target (%8):* `{target:.2f} TL`"
                )
                bulunan_firsatlar.append(mesaj)
        except Exception as e:
            print(f"{hisse} taranırken hata oluştu: {e}")

    # Sonuçları ilet
    if bulunan_firsatlar:
        for f in bulunan_firsatlar:
            telegram_mesaj_gonder(f)
    else:
        # Bağlantıyı test etmek ve çalıştığını görmek için bilgi mesajı atar
        turkey_time = datetime.now(timezone(timedelta(hours=3)))
        zaman_str = turkey_time.strftime('%H:%M - %d.%m.%Y')
        telegram_mesaj_gonder(f"🚀 *BIST Fırsat Avcısı Çalıştı*\nTaraması yapıldı, şu an kriterlere uyan (RSI < 30) hisse bulunamadı.\n⏱ *Zaman:* {zaman_str}")

if __name__ == "__main__":
    piyasa_tara()
