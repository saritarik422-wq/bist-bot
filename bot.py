from datetime import datetime, timezone, timedelta
import os
import csv
import feedparser
import pandas as pd
import requests
import yfinance as yf

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

def tum_bist_hisselerini_getir():
    bist_evreni = [
        "AEFES.IS", "AGHOL.IS", "AKBNK.IS", "AKFGY.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS", "ALBRK.IS", "ALFAS.IS", 
        "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "BERA.IS", "BIMAS.IS", "BRISA.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", 
        "CIMSA.IS", "CWENE.IS", "DOAS.IS", "DOHOL.IS", "ECILC.IS", "ECZYT.IS", "EGEEN.IS", "EKGYO.IS", "ENERY.IS", 
        "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "EUREN.IS", "FROTO.IS", "GARAN.IS", "GESAN.IS", "GLYHO.IS", "GUBRF.IS", 
        "GWIND.IS", "HALKB.IS", "HEKTS.IS", "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISMEN.IS", "IZENR.IS", "KCAER.IS", 
        "KCHOL.IS", "KMPUR.IS", "KONTR.IS", "KONYA.IS", "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "KRDMD.IS", "KZBGY.IS", 
        "MAVI.IS", "MGROS.IS", "ODAS.IS", "ONCSM.IS", "OYAKC.IS", "PENTA.IS", "PETKM.IS", "PGSUS.IS", "QUAGR.IS", 
        "REEDR.IS", "SAHOL.IS", "SASA.IS", "SDTTR.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SOKM.IS", "TAVHL.IS", 
        "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TMSN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUPRS.IS", 
        "TURSG.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS", "YEOTK.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS",
        "OBAMS.IS", "MEGMT.IS", "BORSK.IS", "CATES.IS", "BRKVY.IS", "TABGD.IS", "ARTMS.IS", "LIDER.IS", 
        "BEGYO.IS", "MEKAG.IS", "SURGY.IS", "KBORU.IS", "MARBL.IS", "ALKLC.IS", "DURKN.IS", "HOROZ.IS", 
        "KTSKR.IS", "VAKFN.IS", "BINHO.IS", "ETILR.IS", "FORMT.IS", "GRTRK.IS", "HUBVC.IS"
    ]
    return list(set(bist_evreni))

def kuresel_ve_kap_haberleri_cek():
    haber_ozeti = "Küresel piyasalar, FED/TCMB para politikaları ve yabancı sermaye akışı takip ediliyor."
    try:
        feed = feedparser.parse("https://www.investing.com/rss/news_25.rss")
        if feed.entries:
            haber_ozeti = f"Son Küresel/Yerel Akış: {feed.entries[0].title}"
    except Exception:
        pass
    return haber_ozeti

def log_kaydet(hisse, fiyat, hedef1, hedef2, stop, durum):
    dosya_adi = "log.csv"
    dosya_varmi = os.path.isfile(dosya_adi)
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    with open(dosya_adi, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not dosya_varmi:
            writer.writerow(["Tarih", "Hisse", "Fiyat", "Hedef_1_%3", "Hedef_2_%5", "Stop_Loss", "Durum"])
        writer.writerow([turkey_time.strftime('%Y-%m-%d %H:%M'), hisse, fiyat, hedef1, hedef2, stop, durum])

def nihai_sinirsiz_sistem():
    print("Bütün BIST Evrenini Kapsayan Mühürlü Günlük Bot Başlatılıyor...")
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    saat, dakika = turkey_time.hour, turkey_time.minute
    
    if not (10 <= saat < 18):
        print("Borsa kapalı saat diliminde.")
        return
    if saat == 10 and dakika < 15:
        print("Seans açılış manipülasyon penceresi, bot beklemede.")
        return
    if saat == 12 and 30 <= dakika <= 59:
        print("Öğle arası, bot beklemede.")
        return

    piyasa_gundemi = kuresel_ve_kap_haberleri_cek()
    bulunan_firsatlar = []
    tum_hisseler = tum_bist_hisselerini_getir()

    for hisse in tum_hisseler:
        try:
            data = yf.download(hisse, period="1mo", interval="1d", progress=False)
            if data.empty or len(data) < 20:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            son_fiyat = data['Close'].iloc[-1]
            onceki_fiyat = data['Close'].iloc[-2]
            gunluk_degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100

            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            son_rsi = rsi.iloc[-1]

            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            data['Volume_SMA10'] = data['Volume'].rolling(window=10).mean()
            hacim_patlamasi = data['Volume'].iloc[-1] >= (data['Volume_SMA10'].iloc[-1] * 1.3)

            sma20 = data['Close'].rolling(window=20).mean()
            std20 = data['Close'].rolling(window=20).std()
            bandwidth = ((sma20 + (std20 * 2)) - (sma20 - (std20 * 2))) / sma20
            siskisma_var = bandwidth.iloc[-1] < bandwidth.rolling(window=10).mean().iloc[-1]

            tr = pd.concat([data['High'] - data['Low'], (data['High'] - data['Close'].shift()).abs(), (data['Low'] - data['Close'].shift()).abs()], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            dinamik_stop = son_fiyat - (1.5 * atr)
            hedef_1 = son_fiyat * 1.03
            hedef_2 = son_fiyat * 1.05

            kosul_saglandi = (
                -2.5 <= gunluk_degisim <= 1.5 and
                (hacim_patlamasi or siskisma_var) and
                macd.iloc[-1] > signal.iloc[-1] and
                son_rsi < 48
            )

            if kosul_saglandi:
                rapor = (
                    f"💎 *BOD - MÜHÜRLÜ GÜNLÜK SİNYAL*\n"
                    f"📈 *Hisse:* `{hisse}`\n"
                    f"├ 💵 *Güncel Fiyat:* `{son_fiyat:.2f} TL` (`%{gunluk_degisim:+.2f}`)\n"
                    f"├ 🎯 *Hedef 1 (Yarı Satış %3):* `{hedef_1:.2f} TL`\n"
                    f"├ 🚀 *Hedef 2 (Trend %5):* `{hedef_2:.2f} TL`\n"
                    f"├ 🛡 *ATR İz Süren Stop:* `{dinamik_stop:.2f} TL`\n"
                    f"└ 📊 *Onaylar:* 🔥 Hacim/Sıkışma | 🟢 MACD/RSI Dip"
                )
                bulunan_firsatlar.append(rapor)
                log_kaydet(hisse, round(son_fiyat, 2), round(hedef_1, 2), round(hedef_2, 2), round(dinamik_stop, 2), "BOD Mühürlü Onaylı")
        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")

    zaman_str = turkey_time.strftime('%H:%M - %d.%m.%Y')
    if bulunan_firsatlar:
        for f in bulunan_firsatlar[:3]:
            telegram_mesaj_gonder(f)
        telegram_mesaj_gonder(f"🌐 *KÜRESEL PİYASA & TAHTACI RADARI*\n📌 *Gelişme:* {piyasa_gundemi}\n⏱ *Zaman:* {zaman_str}")
    else:
        telegram_mesaj_gonder(f"🧠 *Günlük BOD Tarama Raporu*\n• {piyasa_gundemi}\n• Tüm BIST evreni tarandı, mühürlü koşullar bekleniyor.\n⏱ *Zaman:* {zaman_str}")

if __name__ == "__main__":
    nihai_sinirsiz_sistem()
