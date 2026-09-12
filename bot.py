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
        print("HATA: Telegram Token veya Chat ID eksik!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram Yanıt Kodu: {response.status_code}")
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")


def tum_bist_hisselerini_getir():
    bist_evreni = [
        "AEFES.IS", "AGHOL.IS", "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS",
        "CIMSA.IS", "CWENE.IS", "DOAS.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS",
        "GWIND.IS", "HALKB.IS", "HEKTS.IS", "KCHOL.IS", "KMPUR.IS", "KONTR.IS",
        "MAVI.IS", "MGROS.IS", "ODAS.IS", "REEDR.IS", "SAHOL.IS", "SASA.IS",
        "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TURSG.IS", "ULKER.IS", "VAKBN.IS",
        "OBAMS.IS", "MEGMT.IS", "BORSK.IS", "BEGYO.IS", "MEKAG.IS", "SURGY.IS",
        "KTSKR.IS", "VAKFN.IS", "BINHO.IS"
    ]
    return list(set(bist_evreni))

def kuresel_ve_kap_haberleri_cek():
    haber_ozeti = "Piyasa akışı ve haberler takip ediliyor."
    try:
        feed = feedparser.parse("https://www.kap.org.tr/tr/rss")
        if feed.entries:
            haber_ozeti = f"Son KAP Bildirimi: {feed.entries[0].title}"
    except Exception:
        pass
    return haber_ozeti

def log_kaydet(hisse, fiyat, hedef1, hedef2, stop, poz_notu):
    dosya_adi = "log.csv"
    dosya_varmi = os.path.isfile(dosya_adi)
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    with open(dosya_adi, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not dosya_varmi:
            writer.writerow(["Tarih", "Hisse", "Fiyat", "Hedef 1", "Hedef 2", "Stop", "Kurumsal Not"])
        writer.writerow([turkey_time.strftime('%Y-%m-%d %H:%M'), hisse, fiyat, hedef1, hedef2, stop, poz_notu])

def kurumsal_akis_sistemi():
    print("Mühürlü Kurumsal RSI(7) Sistemi ve Bağlantı Testi Çalıştırılıyor...")
    
    # 1. Önce o beklenen "Test Test" bağlantı mesajını gönderelim
    telegram_test_mesaji_gonder()

    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    piyasa_gundemi = kuresel_ve_kap_haberleri_cek()
    bulunan_firsatlar = []
    tum_hisseler = tum_bist_hisselerini_getir()

    for hisse in tum_hisseler:
        try:
            data = yf.download(hisse, period="30d", interval="1d", progress=False)
            if data.empty or len(data) < 20:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            son_fiyat = float(data['Close'].iloc[-1])
            onceki_fiyat = float(data['Close'].iloc[-2])
            gunluk_degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100

            # Akıllı Para ve Para Girişi (Money Flow)
            data['Typical_Price'] = (data['High'] + data['Low'] + data['Close']) / 3
            data['Money_Flow'] = data['Typical_Price'] * data['Volume']
            pos_flow = data['Money_Flow'].where(data['Close'] > data['Close'].shift(1), 0).rolling(window=5).sum()
            neg_flow = data['Money_Flow'].where(data['Close'] < data['Close'].shift(1), 0).rolling(window=5).sum()
            mfi_guclu = bool(pos_flow.iloc[-1] > neg_flow.iloc[-1])

            # Teknik Göstergeler (MACD, RSI 7, Hacim, Sıkışma)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
            rs = gain / loss
            rsi7 = 100 - (100 / (1 + rs))
            son_rsi7 = float(rsi7.iloc[-1])

            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()

            data['Volume_SMA10'] = data['Volume'].rolling(window=10).mean()
            hacim_patlamasi = bool(data['Volume'].iloc[-1] > (data['Volume_SMA10'].iloc[-1] * 1.4))

            sma20 = data['Close'].rolling(window=20).mean()
            std20 = data['Close'].rolling(window=20).std()
            bandwidth = ((sma20 + (std20 * 2)) - (sma20 - (std20 * 2))) / sma20
            siskisma_var = bool(bandwidth.iloc[-1] < bandwidth.rolling(window=10).mean().iloc[-1])

            # ATR Dinamik Stop ve Hedefler
            tr = pd.concat([data['High'] - data['Low'], 
                            abs(data['High'] - data['Close'].shift()), 
                            abs(data['Low'] - data['Close'].shift())], axis=1).max(axis=1)
            atr = float(tr.rolling(window=14).mean().iloc[-1])
            dinamik_stop = round(son_fiyat - (atr * 1.5), 2)
            hedef_1 = round(son_fiyat * 1.03, 2)
            hedef_2 = round(son_fiyat * 1.05, 2)

            # Dinamik Pozisyon Boyutlandırma (Risk Yönetimi)
            risk_mesafesi = son_fiyat - dinamik_stop
            if risk_mesafesi <= 0:
                risk_mesafesi = son_fiyat * 0.02
            
            toplam_risk_butcesi = 2000.0  # 100 bin TL kasa için %2 risk
            onerilen_lot = int(toplam_risk_butcesi / risk_mesafesi)
            onerilen_tutar = int(onerilen_lot * son_fiyat)

            # Mühürlü Günlük Kurumsal Koşul Seti (RSI 7 ile)
            kurumsal_kosul = (
                -2.5 <= gunluk_degisim <= 5.0 and
                (hacim_patlamasi or siskisma_var) and
                float(macd.iloc[-1]) > float(signal.iloc[-1]) and
                son_rsi7 < 48 and
                mfi_guclu
            )

            if kurumsal_kosul:
                rapor = (
                    f"🚨 *MÜHÜRLÜ RSI7 - FIRSAT RAPORU*\n"
                    f"📈 *Hisse Kod:* `{hisse}`\n"
                    f"┣ 💵 *Güncel Fiyat:* {son_fiyat:.2f} TL\n"
                    f"┣ 📊 *RSI(7) Değeri:* {son_rsi7:.1f}\n"
                    f"┣ 🎯 *Hedef 1:* {hedef_1} TL | *Hedef 2:* {hedef_2} TL\n"
                    f"┣ 🛡️ *İz Süren Stop:* {dinamik_stop} TL\n"
                    f"┣ 💰 *Akıllı Para (MFI):* Sinyal Alındı ✅\n"
                    f"┗ 📐 *Önerilen Pozisyon Tutar:* ~{onerilen_tutar} TL ({onerilen_lot} Lot)"
                )
                bulunan_firsatlar.append(rapor)
                log_kaydet(hisse, son_fiyat, hedef_1, hedef_2, dinamik_stop, f"RSI7 Tutar: {onerilen_tutar} TL")
        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")

    zaman_str = turkey_time.strftime('%H:%M - %d.%m.%Y')
    
    if bulunan_firsatlar:
        for f in bulunan_firsatlar[:3]:
            telegram_mesaj_gonder(f)
    else:
        durum_raporu = (    
            # --- Test / Çalışma Bildirimi 

    
    payload = {
        "chat_id": CHAT_ID,
        "text": "🟢 bot.py başarıyla çalıştı ve taramayı tamamladı!"
    }
    requests.post(url, json=payload)

            "🧠 *GÜNLÜK PİYASA DURUM RAPORU (RSI 7)*\n"
            f"• Küresel/Yerel Akış: {piyasa_gundemi}\n"
            "• Mühürlü RSI(7) koşulları taranıyor, uygun formasyon bekleniyor.\n"
            f"⏱️ *Zaman:* {zaman_str}"
        )
        telegram_mesaj_gonder(durum_raporu)

if __name__ == "__main__":
    kurumsal_akis_sistemi()


