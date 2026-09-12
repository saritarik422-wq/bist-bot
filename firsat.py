from datetime import datetime, timezone, timedelta
import os
import requests
import yfinance as yf
import pandas as pd

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def telegram_mesaj_gonder(mesaj):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("HATA: Telegram Token veya Chat ID tanımlanmamış!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Yanıt Kodu: {response.status_code}")
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def firsat_py_orta_vade_taramasi():
    print("Fırsat PY (Orta Vadeli Hisseler) Taraması Başlatılıyor...")
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    zaman_str = turkey_time.strftime('%H:%M - %d.%m.%Y')
    
    orta_vade_havuzu = ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "TUPRS.IS", "GARAN.IS", "EREGL.IS", "BIMAS.IS", "FROTO.IS", "SAHOL.IS", "SISE.IS"]
    secilenler = []

    for hisse in orta_vade_havuzu:
        try:
            data = yf.download(hisse, period="3mo", interval="1d", progress=False)
            if data.empty or len(data) < 30:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            son_fiyat = data['Close'].iloc[-1]
            ma5 = data['Close'].rolling(window=5).mean().iloc[-1]
            ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
            
            if son_fiyat > ma20 and data['Close'].iloc[-1] >= ma5 * 0.99:
                hedef_orta = son_fiyat * 1.07
                stop_orta = son_fiyat * 0.96
                secilenler.append(f"• `{hisse}` | Fiyat: `{son_fiyat:.2f} TL` | Hedef: `{hedef_orta:.2f} TL`")
        except Exception as e:
            print(f"Orta vade tarama hatası {hisse}: {e}")

    if secilenler:
        rapor = (
            f"🛡 *FIRSAT PY - ORTA VADELİ SEPET (2-5 GÜNLÜK)*\n"
            f"📌 *Durum:* Orta vadeli periyotta nakiti değerlendirecek güçlü adaylar listelendi.\n"
            f"📦 *Aday Hisseler:*\n" + "\n".join(secilenler[:3]) + f"\n⏱ *Zaman:* {zaman_str}"
        )
        telegram_mesaj_gonder(rapor)
    else:
        telegram_mesaj_gonder(f"🛡 *Fırsat PY Raporu*\n• Orta vade havuzu tarandı, uygun formasyon bekleniyor.\n⏱ *Zaman:* {zaman_str}")

if __name__ == "__main__":
    firsat_py_orta_vade_taramasi()
