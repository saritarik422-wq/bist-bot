from datetime import datetime, timezone, timedelta
import os
import feedparser
import pandas as pd
import requests
import yfinance as yf

# --- GÜVENLİ TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def telegram_mesaj_gonder(mesaj):
    """Telegram üzerinden anlık ve biçimlendirilmiş bildirim gönderir."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print(
            "Telegram Token veya Chat ID bulunamadı. Lütfen GitHub Secrets ayarlarını kontrol edin."
        )
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def borsa_acik_mi():
    """Zaman / Seans Kontrolü: Borsa İstanbul (UTC+3) çalışma saatlerini kontrol eder."""
    tr_zaman = datetime.now(timezone(timedelta(hours=3)))
    if tr_zaman.weekday() >= 5:  # Hafta sonu
        return False
    dakika_cinsinden = tr_zaman.hour * 60 + tr_zaman.minute
    if 600 <= dakika_cinsinden <= 1080:  # 10:00 - 18:00 arası
        return True
    return False

def borsa_istanbul_tum_hisseleri_getir():
    """BIST'teki hisseleri içeren geniş havuz."""
    genis_havuz = [
        "THYAO.IS",
        "EREGL.IS",
        "KCHOL.IS",
        "GARAN.IS",
        "AKBNK.IS",
        "ASELS.IS",
        "PETKM.IS",
        "TUPRS.IS",
        "SASA.IS",
        "HEKTS.IS",
        "YKBNK.IS",
        "ISCTR.IS",
        "BIMAS.IS",
        "MGROS.IS",
        "TOASO.IS",
        "FROTO.IS",
        "SISE.IS",
        "ENKAI.IS",
        "KRDMD.IS",
        "ASTOR.IS",
    ]
    return genis_havuz

def rsi_hesapla(veri, periyot=7):
    delta = veri["Close"].diff()
    kazanc = delta.where(delta > 0, 0).rolling(window=periyot).mean()
    kayyip = (-delta.where(delta < 0, 0)).rolling(window=periyot).mean()
    rs = kazanc / kayyip
    rsi = 100 - (100 / (1 + rs))
    return rsi

def sinirsiz_firsat_avcisi():
    if not borsa_acik_mi():
        print("Borsa kapalı. Fırsat avcısı beklemede.")
        return

    print("--- Test Modu: BİST Fırsat Avcısı Çalışıyor ---")
    tum_hisseler = borsa_istanbul_tum_hisseleri_getir()

    for hisse in tum_hisseler:
        try:
            df = yf.download(hisse, period="5d", interval="1d", progress=False)
            if df.empty:
                continue

            df["RSI_7"] = rsi_hesapla(df, periyot=7)
            son_rsi = df["RSI_7"].iloc[-1]
            son_fiyat = df["Close"].iloc[-1]

            # GEÇİCİ TEST FİLTRESİ: İlk taranan hissede direkt test mesajı atar
            hedef_fiyat = son_fiyat * 1.025
            stop_fiyat = son_fiyat * 0.985

            uyari = (
                f"🎯 *[TEST BİLDİRİMİ - SİSTEM ÇALIŞIYOR]*\n"
                f"📌 Hisse: `{hisse}`\n"
                f"💵 Anlık Fiyat: `{son_fiyat:.2f}` TL\n"
                f"📊 RSI-7: `{son_rsi:.2f}`\n"
                f"🎯 Hedef Fiyat (%2.5): `{hedef_fiyat:.2f}` TL\n"
                f"🛑 Stop-Loss (%1.5): `{stop_fiyat:.2f}` TL\n"
                f"🚀 *Aksiyon:* Telegram bağlantısı başarılı!"
            )
            print(f"-> TEST MESAJI GÖNDERİLİYOR: {hisse}")
            telegram_mesaj_gonder(uyari)
            break  # Sadece ilk hissede test edip durdurur

        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")

if __name__ == "__main__":
    sinirsiz_firsat_avcisi()
