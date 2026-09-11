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

def kuresel_finans_ve_tahtaci_taramasi():
    """Küresel finans haberlerini, FED, faiz ve piyasa akışını tarar."""
    print("--- Küresel Finans & Tahtacı Taraması Başlatılıyor ---")
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news.rss")
        for entry in feed.entries[:3]:
            baslik = entry.title.upper()
            if any(
                kriter in baslik
                for kriter in [
                    "FED",
                    "FAİZ",
                    "ENFLASYON",
                    "YABANCI",
                    "SERMAYE",
                    "BIST",
                    "TAHTACI",
                ]
            ):
                haber_mesaji = (
                    f"🌐 *[KÜRESEL PİYASA & TAHTACI RADARI]*\n"
                    f"📌 *Gelişme:* `{entry.title}`\n"
                    f"⚡ *Aksiyon:* Makro akışlar takip ediliyor."
                )
                telegram_mesaj_gonder(haber_mesaji)
                break
    except Exception as e:
        print(f"Haber tarama hatası: {e}")

def borsa_istanbul_tum_hisseleri_getir():
    """BIST'teki tüm hisseleri ve yeni halka arzları içeren geniş havuz."""
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
        "BEGYO.IS",
        "OBAMS.IS",
        "LMKDC.IS",
        "ARTMS.IS",
        "CATES.IS",
        "MEGMT.IS",
        "SURGY.IS",
        "VAKBN.IS",
        "HALKB.IS",
        "PGSUS.IS",
        "TCELL.IS",
        "BORSK.IS",
        "EBEBK.IS",
        "KOTON.IS",
        "OZSUB.IS",
        "TABGD.IS",
        "DOHOL.IS",
        "ARCLK.IS",
        "KOZAA.IS",
        "KOZAL.IS",
        "ODAS.IS",
        "BERA.IS",
        "BOBET.IS",
        "VESBE.IS",
        "ALBRK.IS",
    ]
    return genis_havuz

def rsi_hesapla(veri, periyot=7):
    delta = veri["Close"].diff()
    kazanc = delta.where(delta > 0, 0).rolling(window=periyot).mean()
    kayyip = (-delta.where(delta < 0, 0)).rolling(window=periyot).mean()
    rs = kazanc / kayyip
    rsi = 100 - (100 / (1 + rs))
    return rsi

def sinyali_logla(hisse, tip, fiyat, rsi):
    """Yakalanan fırsatları log.csv dosyasına kaydeder."""
    try:
        veri = {
            "Zaman": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Hisse": [hisse],
            "Sinyal_Tipi": [tip],
            "Fiyat": [fiyat],
            "RSI_7": [rsi],
        }
        pd.DataFrame(veri).to_csv("log.csv", mode="a", index=False, header=False)
    except Exception as e:
        print(f"Loglama hatası: {e}")

def sinirsiz_firsat_avcisi():
    if not borsa_acik_mi():
        print("Borsa kapalı. Fırsat avcısı beklemede.")
        return

    print("--- Sınırsız BİST Fırsat Avcısı Çalışıyor ---")
    kuresel_finans_ve_tahtaci_taramasi()

    tum_hisseler = borsa_istanbul_tum_hisseleri_getir()
    bulunan_firsat_sayisi = 0

    for hisse in tum_hisseler:
        try:
            df = yf.download(hisse, period="5d", interval="1d", progress=False)
            if df.empty:
                continue

            df["RSI_7"] = rsi_hesapla(df, periyot=7)
            son_rsi = df["RSI_7"].iloc[-1]
            son_fiyat = df["Close"].iloc[-1]

            # Hacim Onayı (Volume Spike)
            ortalama_hacim = df["Volume"].rolling(window=5).mean().iloc[-1]
            anlik_hacim = df["Volume"].iloc[-1]
            hacim_onayi = anlik_hacim > ortalama_hacim

            # TETİK: RSI-7 Dip Dönüşü (30-40 Aralığı + Hacim)
            if 30 <= son_rsi <= 40 and hacim_onayi:
                bulunan_firsat_sayisi += 1
                hedef_fiyat = son_fiyat * 1.025
                stop_fiyat = son_fiyat * 0.985

                uyari = (
                    f"🎯 *[SINIRSIZ BİST DİP FIRSATI]*\n"
                    f"📌 Hisse: `{hisse}`\n"
                    f"💵 Anlık Fiyat: `{son_fiyat:.2f}` TL\n"
                    f"📊 RSI-7: `{son_rsi:.2f}`\n"
                    f"🎯 Hedef Fiyat (%2.5): `{hedef_fiyat:.2f}` TL\n"
                    f"🛑 Stop-Loss (%1.5): `{stop_fiyat:.2f}` TL\n"
                    f"🚀 *Aksiyon:* Fırsatı değerlendirebilirsin!"
                )
                print(f"-> FIRSAT BULUNDU: {hisse}")
                telegram_mesaj_gonder(uyari)
                sinyali_logla(hisse, "DIP_DONUS", son_fiyat, son_rsi)

            # TETİK: Tepe / Aşırı Alım Noktası (RSI >= 80)
            elif son_rsi >= 80:
                uyari = (
                    f"🚨 *[AŞIRI ALIM / KÂR AL BÖLGESİ]*\n"
                    f"📌 Hisse: `{hisse}`\n"
                    f"💵 Anlık Fiyat: `{son_fiyat:.2f}` TL\n"
                    f"📊 RSI-7: `{son_rsi:.2f}`\n"
                    f"💰 *Aksiyon:* Kârı cebe atma vakti!"
                )
                print(f"-> TEPE NOKTASI: {hisse}")
                telegram_mesaj_gonder(uyari)
                sinyali_logla(hisse, "KAR_AL", son_fiyat, son_rsi)

        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")

    print(f"--- Geniş Tarama Tamamlandı. Toplam {bulunan_firsat_sayisi} fırsat yakalandı. ---")

if __name__ == "__main__":
    sinirsiz_firsat_avcisi()
