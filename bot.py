import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import feedparser
import csv

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
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Yanıt Kodu: {response.status_code}")
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def tum_bist_hisselerini_getir():
    bist_evreni = [
        "AEFES.IS", "AGHOL.IS", "AKBNK.IS", "AKCNS.IS", "AKENR.IS", "AKFYE.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS", "ALBRK.IS", "ALFAS.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "BERA.IS", "BIMAS.IS", "BOBET.IS", "BRSAN.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", "CIMSA.IS", "CWENE.IS", "DOAS.IS", "DOHOL.IS", "EBEBK.IS", "ECILC.IS", "EGEEN.IS", "EKGYO.IS", "ENJSA.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "EUREN.IS", "FROTO.IS", "GARAN.IS", "GESAN.IS", "GLYHO.IS", "GOKNR.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS", "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISMEN.IS", "IZMDC.IS", "KCAER.IS", "KCHOL.IS", "KONTR.IS", "KONYA.IS", "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "KRDMD.IS", "KZBGY.IS", "MAVI.IS", "MGROS.IS", "ODAS.IS", "OTKAR.IS", "OYAKC.IS", "PERA.IS", "PETKM.IS", "PGSUS.IS", "PSGYO.IS", "QUAGR.IS", "SAHOL.IS", "SASA.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SOKM.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TMSN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUPRS.IS", "TURSG.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS",
        "OBAMS.IS", "MEGMT.IS", "BORSK.IS", "KTSRK.IS", "VAKFN.IS", "BINHO.IS"
    ]
    return list(set(bist_evreni))

def kuresel_ve_kap_haberleri_cek():
    haber_ozeti = "Piyasa akışı ve haberler taranıyor..."
    try:
        feed = feedparser.parse("https://www.kap.org.tr/tr/sirket-bildirimleri")
        if feed.entries:
            haber_ozeti = f"Son KAP Bildirimi: {feed.entries[0].title}"
    except Exception:
        pass
    return haber_ozeti

def log_kaydet(hisse, fiyat, hedef1, hedef2, stop):
    dosya_adi = "bot_log.csv"
    dosya_varmi = os.path.isfile(dosya_adi)
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    with open(dosya_adi, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not dosya_varmi:
            writer.writerow(["Tarih", "Hisse", "Fiyat", "Hedef 1", "Hedef 2", "Dinamik Stop"])
        writer.writerow([turkey_time.strftime('%Y-%m-%d %H:%M'), hisse, fiyat, hedef1, hedef2, stop])

# --- 1. MODÜL: GÜNÜN MÜHÜRLÜ BOT ---
def kurumsal_akis_sistemi():
    print("Kurumsal Akıllı Para (Smart Money) sistemi çalıştırılıyor...")
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    
    piyasa_gundemi = kuresel_ve_kap_haberleri_cek()
    bulunan_firsatlar = []
    tum_hisseler = tum_bist_hisselerini_getir()
    
    for hisse in tum_hisseler:
        try:
            data = yf.download(hisse, period="6mo", interval="1d", progress=False)
            if data.empty or len(data) < 50:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            son_fiyat = float(data['Close'].iloc[-1])
            onceki_fiyat = float(data['Close'].iloc[-2])
            gunluk_degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
            
            data['Typical_Price'] = (data['High'] + data['Low'] + data['Close']) / 3
            data['Money_Flow'] = data['Typical_Price'] * data['Volume']
            pos_flow = data['Money_Flow'].where(data['Typical_Price'] > data['Typical_Price'].shift(1), 0)
            neg_flow = data['Money_Flow'].where(data['Typical_Price'] < data['Typical_Price'].shift(1), 0)
            mfi_guclu = bool(pos_flow.iloc[-1] > neg_flow.iloc[-1])
            
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi14 = 100 - (100 / (1 + rs))
            son_rsi14 = float(rsi14.iloc[-1])
            
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            kural_3_macd = bool(macd.iloc[-1] > signal.iloc[-1])
            
            data['Volume_SMA10'] = data['Volume'].rolling(window=10).mean()
            hacim_patlamasi = bool(data['Volume'].iloc[-1] > (data['Volume_SMA10'].iloc[-1] * 1.5))
            
            sma20 = data['Close'].rolling(window=20).mean()
            std20 = data['Close'].rolling(window=20).std()
            bandwidth = ((sma20 + (std20 * 2)) - (sma20 - (std20 * 2))) / sma20
            siskisma_var = bool(bandwidth.iloc[-1] < bandwidth.rolling(window=20).mean().iloc[-1])
            kural_2_hacim_sikisma = bool(hacim_patlamasi or siskisma_var)
            
            tr = pd.concat([data['High'] - data['Low'], 
                            abs(data['High'] - data['Close'].shift()), 
                            abs(data['Low'] - data['Close'].shift())], axis=1).max(axis=1)
            atr = float(tr.rolling(window=14).mean().iloc[-1])
            dinamik_stop = round(son_fiyat - (atr * 1.5), 2)
            hedef_1 = round(son_fiyat * 1.035, 2)
            hedef_2 = round(son_fiyat * 1.07, 2)
            
            risk_mesafesi = son_fiyat - dinamik_stop
            if risk_mesafesi <= 0:
                risk_mesafesi = son_fiyat * 0.05
                
            toplam_risk_butcesi = 2000.0
            onerilen_lot = int(toplam_risk_butcesi / risk_mesafesi)
            onerilen_tutar = int(onerilen_lot * son_fiyat)
            
            kurumsal_kosul = (
                -2.5 <= gunluk_degisim <= 8.5 and
                (hacim_patlamasi or siskisma_var) and
                float(macd.iloc[-1]) > float(signal.iloc[-1]) and
                son_rsi14 < 48 and
                mfi_guclu
            )
            
            if kurumsal_kosul:
                rapor_parca = (
                    f"💎 *BOD - GÜNLÜK KURUMSAL AKIŞ*\n"
                    f"📈 *Hisse:* `{hisse}`\n"
                    f"💵 *Güncel Fiyat:* `{son_fiyat:.2f} TL`\n"
                    f"🎯 *Hedef 1:* `{hedef_1} TL` | *Hedef 2:* `{hedef_2} TL`\n"
                    f"🛡️ *ATR İz Süren Stop:* `{dinamik_stop} TL`\n"
                    f"💰 *Akıllı Para Girişi:* `Onaylandı`\n"
                    f"📊 *Kurumsal Pozisyon:* `{onerilen_lot} Lot ({onerilen_tutar} TL)`"
                )
                bulunan_firsatlar.append(rapor_parca)
                log_kaydet(hisse, son_fiyat, hedef_1, hedef_2, dinamik_stop)
                
        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")
            
    zaman_str = turkey_time.strftime('%H:%M - %d.%m.%Y')
    
    if bulunan_firsatlar:
        for f in bulunan_firsatlar[:3]:
            telegram_mesaj_gonder(f)
    else:
        durum_raporu = (
            f"🧠 *Tüm BIST Evreni Günlük Tarama Raporu*\n"
            f"• Son Küresel/Yerel Akış: {piyasa_gundemi}\n"
            f"• Günlük mühürlü kurumsal koşullarda fırsat tespit edilemedi.\n"
            f"⏱️ *Zaman:* {zaman_str}"
        )
        telegram_mesaj_gonder(durum_raporu)

# --- 2. MODÜL: ORTA VADE SEPETİ (SMA50 TREND) ---
def orta_vade_sepet_sistemi():
    print("Mühürlü Orta Vadeli Sepet Modülü çalıştırılıyor...")
    turkey_time = datetime.now(timezone(timedelta(hours=3)))
    orta_vade_adaylar = []
    tum_hisseler = tum_bist_hisselerini_getir()
    
    for hisse in tum_hisseler:
        try:
            data = yf.download(hisse, period="1y", interval="1d", progress=False)
            if data.empty or len(data) < 60:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            son_fiyat = float(data['Close'].iloc[-1])
            onceki_fiyat = float(data['Close'].iloc[-2])
            gunluk_degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
            
            data['SMA50'] = data['Close'].rolling(window=50).mean()
            sma50_deger = float(data['SMA50'].iloc[-1])
            ana_trend_ustunde = bool(son_fiyat > sma50_deger)
            
            kural_1_degisim = (-3.0 <= gunluk_degisim <= 6.0)
            
            data['Volume_SMA20'] = data['Volume'].rolling(window=20).mean()
            hacim_sikisma = bool(data['Volume'].iloc[-1] < data['Volume_SMA20'].iloc[-1])
            kural_2_hacim_sikisma = bool(hacim_sikisma or data['Volume'].iloc[-1] > data['Volume_SMA20'].iloc[-1])
            
            exp1 = data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            kural_3_macd = bool(macd.iloc[-1] >= signal.iloc[-1])
            
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi14 = 100 - (100 / (1 + rs))
            son_rsi14 = float(rsi14.iloc[-1])
            
            data['Typical_Price'] = (data['High'] + data['Low'] + data['Close']) / 3
            data['Money_Flow'] = data['Typical_Price'] * data['Volume']
            pos_flow = data['Money_Flow'].where(data['Typical_Price'] > data['Typical_Price'].shift(1), 0)
            neg_flow = data['Money_Flow'].where(data['Typical_Price'] < data['Typical_Price'].shift(1), 0)
            mfi_guclu = bool(pos_flow.iloc[-1] >= neg_flow.iloc[-1])
            
            kural_4_para_ve_rsi = bool(son_rsi14 < 55 and mfi_guclu)
            
            orta_vade_mushur = (
                ana_trend_ustunde and
                kural_1_degisim and
                kural_2_hacim_sikisma and
                kural_3_macd and
                kural_4_para_ve_rsi
            )
            
            if orta_vade_mushur:
                orta_vade_adaylar.append(f"• `{hisse}` (Fiyat: {son_fiyat:.2f} TL)")
                log_kaydet(hisse, son_fiyat, son_fiyat*1.05, son_fiyat*1.10, son_fiyat*0.95)
                
        except Exception as e:
            print(f"{hisse} orta vade taranırken hata: {e}")
            
    zaman_str = turkey_time.strftime('%H:%M - %d.%m.%Y')
    
    if orta_vade_adaylar:
        sepet_metni = "\n".join(orta_vade_adaylar)
        rapor = (
            f"🛡️ *FIRSAT PY - ORTA VADELİ SEPET*\n"
            f"📌 *Durum:* Orta vadeli trendde\n"
            f"📦 *Aday Hisseler:*\n{sepet_metni}\n"
            f"⏱️ *Zaman:* {zaman_str}"
        )
        telegram_mesaj_gonder(rapor)
    else:
        print("Orta vade sepet kriterlerine uyan hisse bulunamadı.")

if __name__ == "__main__":
    telegram_mesaj_gonder("🚀 Tarık Bey, sistem mühürlendi ve Telegram bağlantısı başarıyla sağlandı!")
    kurumsal_akis_sistemi()
    orta_vade_sepet_sistemi()
