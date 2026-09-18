from fon_yoneticisi import STABLE_FUNDS, GROWTH_FUNDS, fon_karar_mekanizmasi
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import csv
import time

# --- TELEGRAM AYARLARI ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def telegram_mesaj_gonder(mesaj):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("HATA: Telegram Token veya Chat ID sistem ortamında bulunamadı!")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    
    # Mesaj gitmeme sorununa karşı 3 kez tekrar deneme (Retry) mekanizması
    for deneme in range(3):
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                print("Telegram mesajı başarıyla iletildi.")
                return True
            else:
                print(f"Telegram mesajı gönderilemedi (Kod: {response.status_code}), Tekrar deneniyor... ({deneme+1}/3)")
        except Exception as e:
            print(f"Telegram bağlantı istisnası: {e}, Tekrar deneniyor... ({deneme+1}/3)")
        time.sleep(2)
        
    print("KRİTİK HATA: Telegram mesajı 3 denemede de iletilemedi!")
    return False

def tum_bist_hisselerini_getir():
    bist_genis_evren = [
        "AEFES.IS", "AGHOL.IS", "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS", "AKENR.IS", "AKFGY.IS", "AKGRT.IS", 
        "AKSA.IS", "AKSEN.IS", "ALARK.IS", "ALBRK.IS", "ALFAS.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", 
        "BERA.IS", "BIMAS.IS", "BOBET.IS", "BRISA.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", "CEMTS.IS", 
        "CIMSA.IS", "CLEBI.IS", "CWENE.IS", "DEVA.IS", "DOAS.IS", "DOHOL.IS", "ECILC.IS", "ECZYT.IS", 
        "EGEEN.IS", "EFORC.IS", "EKGYO.IS", "ENERY.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "EYYG.IS", 
        "FROTO.IS", "GARAN.IS", "GESAN.IS", "GLYHO.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS", 
        "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISGYO.IS", "KCHOL.IS", "KMPUR.IS", "KONTR.IS", "KONYA.IS", 
        "KOZAA.IS", "KOZAL.IS", "KRDMD.IS", "KZBGY.IS", "MAVI.IS", "MGROS.IS", "MPARK.IS", "OBAMS.IS", 
        "ODAS.IS", "ONCSM.IS", "OTKAR.IS", "OYAKC.IS", "PAKD.IS", "PASEU.IS", "PETKM.IS", "PGSUS.IS", 
        "QUAGR.IS", "REEDR.IS", "SAHOL.IS", "SASA.IS", "SDTTR.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", 
        "SOKM.IS", "TABGD.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TMSN.IS", "TOASO.IS", 
        "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUPRS.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS", 
        "YYLGD.IS", "YKBNK.IS", "ZOREN.IS"
    ]
    return list(set(bist_genis_evren))

def log_kaydet(hisse, fiyat, hedef, stop, skor):
    try:
        dosya_adi = "bot_log_alpha.csv"
        dosya_varmi = os.path.isfile(dosya_adi)
        turkey_time = datetime.now(timezone(timedelta(hours=3)))
        with open(dosya_adi, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not dosya_varmi:
                writer.writerow(["Tarih", "Hisse", "Fiyat", "Hedef1", "DinamikStop", "LiderlikSkoru"])
            writer.writerow([turkey_time.strftime('%Y-%m-%d %H:%M'), hisse, fiyat, hedef, stop, skor])
    except Exception as e:
        print(f"Log kaydetme hatası: {e}")

def piyasa_kurumsal_filtresi():
    try:
        bist = yf.download("XU100.IS", period="3mo", interval="1d", progress=False)
        if bist.empty:
            return True 
        if isinstance(bist.columns, pd.MultiIndex):
            bist.columns = bist.columns.droplevel(1)
        
        son_fiyat = float(bist['Close'].iloc[-1])
        sma50 = float(bist['Close'].rolling(window=50).mean().iloc[-1])
        
        if son_fiyat < sma50:
            return False
    except Exception as e:
        print(f"Kurumsal piyasa filtresi hatası: {e}")
    return True


# --- ALPHA-PRIME ULTIMATE KURUMSAL MOTOR ---
def alpha_prime_ultimate_motoru():
    print("Alpha-Prime Ultimate Kurumsal Fon Motoru Başlatıldı...")
    
    try:
        if not piyasa_kurumsal_filtresi():
            print("Piyasa (BIST100) Güvenlik Sınırının Altında! Sinyaller bloke edildi.")
            telegram_mesaj_gonder("🛡️ *Alpha-Prime Koruma Kalkanı:* BIST100 ana trend (SMA50) altında olduğu için fon düzeyinde güvenli mod aktif, nakitte bekliyoruz.")
            return
    except Exception as e:
        print(f"Piyasa filtre istisnası: {e}")

    try:
        bist_data = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)
        if isinstance(bist_data.columns, pd.MultiIndex):
            bist_data.columns = bist_data.columns.droplevel(1)
        bist_getiri = bist_data['Close'].pct_change(periods=20).iloc[-1] 
    except:
        bist_getiri = 0

    bulunan_firsatlar = []
    tum_hisseler = tum_bist_hisselerini_getir()
    print(f"Taranan Genişletilmiş Varlık Havuzu: {len(tum_hisseler)}")

    for hisse in tum_hisseler:
        try:
            data = yf.download(hisse, period="6mo", interval="1d", progress=False)
            if data.empty or len(data) < 50:
                continue
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)

            son_fiyat = float(data['Close'].iloc[-1])
            
            # 1. Trend Şartı (Fiyat SMA50 Üzerinde)
            data['SMA50'] = data['Close'].rolling(window=50).mean()
            sma50_deger = float(data['SMA50'].iloc[-1])
            if son_fiyat <= sma50_deger:
                continue  

            # 2. Hacim Kalitesi ve Patlaması
            data['Volume_SMA20'] = data['Volume'].rolling(window=20).mean()
            hacim_ort = float(data['Volume_SMA20'].iloc[-1])
            son_hacim = float(data['Volume'].iloc[-1])
            if son_hacim < (hacim_ort * 1.5):
                continue  

            # 3. Testere Kapanı Önleyici ATR Volatilite Filtresi
            data['TR'] = abs(data['High'] - data['Low'])
            data['ATR14'] = data['TR'].rolling(window=14).mean()
            atr_deger = float(data['ATR14'].iloc[-1])
            if (atr_deger / son_fiyat) < 0.01: 
                continue 

            # 4. Rölatif Güç (RS) - Piyasadan Güçlü Olma Şartı
            hisse_getiri = data['Close'].pct_change(periods=20).iloc[-1]
            if hisse_getiri <= bist_getiri:
                continue 

            liderlik_skoru = round((hisse_getiri - bist_getiri) * 100, 2)
            hedef_1 = round(son_fiyat * 1.07, 2)  
            dinamik_stop = round(sma50_deger, 2)    

            rapor_parca = (
                f"💎 *ALPHA-PRIME ULTIMATE SİNYAL*\n"
                f"📈 *Hisse:* `{hisse}`\n"
                f"💰 *Güncel Fiyat:* `{son_fiyat:.2f} TL`\n"
                f"⚡ *Liderlik Skoru (RS):* `+{liderlik_skoru}%`\n"
                f"🎯 *1. Kademeli Hedef:* `{hedef_1} TL`\n"
                f"🛑 *İz Süren Stop (SMA50):* `{dinamik_stop} TL`\n"
                f"🛡️ *Durum:* Testere Kapanı Atlatıldı, Fon Onaylı Lider Trend!"
            )
            bulunan_firsatlar.append((liderlik_skoru, rapor_parca, hisse, son_fiyat, hedef_1, dinamik_stop))
            log_kaydet(hisse, son_fiyat, hedef_1, dinamik_stop, liderlik_skoru)
            
            time.sleep(0.3)

        except Exception as e:
            continue

    try:
        if bulunan_firsatlar:
            bulunan_firsatlar.sort(key=lambda x: x[0], reverse=True)
            for skor, rapor, hisse, fiyat, hedef, stop in bulunan_firsatlar[:3]:
                telegram_mesaj_gonder(rapor)
        else:
            print("Kurumsal kriterlere uyan lider varlık bulunamadı (Testere piyasasından korundu).")
    except Exception as e:
        print(f"Rapor iletme hatası: {e}")


if __name__ == "__main__":
    try:
        telegram_mesaj_gonder("🔔 *Sistem Başlatıldı*...")
        
        # 1. Önce Alpha-Prime Hisse Taramasını Çalıştır
        alpha_prime_ultimate_motoru()
        
        # 2. Ardından Fortress Fon Karar Mekanizmasını Çalıştır ve Raporla
        durum, aktif_sepet = fon_karar_mekanizmasi()
        fon_raporu = (
            f"🛡️ **FORTRESS FON DURUM RAPORU** 🛡️\n\n"
            f"📊 **BIST100 Trend:** {durum}\n"
            f"🧺 **Aktif Fon Sepeti:** {', '.join(aktif_sepet)}"
        )
        print(fon_raporu)
        telegram_mesaj_gonder(fon_raporu)
        
    except Exception as e:
        print(f"Kritik Başlatma Hatası: {e}")




