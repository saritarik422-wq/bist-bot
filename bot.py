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
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        print("Galaktik İstihbarat Raporu başarıyla iletildi komutan!")
    except Exception as e:
        print(f"Telegram mesajı gönderilirken hata oluştu: {e}")

def get_live_macd_and_rsi(ticker_symbol):
    """
    Yahoo Finance üzerinden BİST verisini çekip 12/26/9 MACD, 14 RSI ve Günlük Değişimi hesaplar.
    MultiIndex veri yapısı ve .IS uzantısı otomatik düzeltilir.
    """
    try:
        symbol = ticker_symbol if ticker_symbol.endswith(".IS") else f"{ticker_symbol}.IS"
        df = yf.download(symbol, period="6m", interval="1d", progress=False)
        
        if df.empty or len(df) < 15:
            return None, None, None, None
        
        # MultiIndex sütun yapısını düzleştirme
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        close_series = df['Close'].dropna()
        if len(close_series) < 15:
            return None, None, None, None

        last_price = float(close_series.iloc[-1])
        prev_close = float(close_series.iloc[-2])
        daily_change = ((last_price - prev_close) / prev_close) * 100
        
        # EMA & MACD Hesaplama (12, 26, 9)
        exp12 = close_series.ewm(span=12, adjust=False).mean()
        exp26 = close_series.ewm(span=26, adjust=False).mean()
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
        else:
            macd_status = "🔴 SAT / NÖTR"

        # RSI Hesaplama (14 Günlük)
        delta = close_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        last_rsi = round(float(rsi.iloc[-1]), 1)

        return last_price, last_rsi, macd_status, daily_change
    except Exception as e:
        print(f"{ticker_symbol} hatası: {e}")
        return None, None, None, None

def generate_pure_bist_battle_report():
    try:
        tarih = datetime.now().strftime("%d.%m.%Y")
        
        # 1. ÇEKİRDEK LİDER HİSSELER (Sabit Portföy Amiralleri)
        cekirdek_hisseler = ["THYAO", "ASELS", "KCHOL", "TUPRS", "BIMAS"]
        
        # 2. BİST 30 / BİST 50 / BİST 100 TAM TARAMA HAVUZU + TAZE HALKA ARZLAR
        bist100_tarama_havuzu = list(set([
            # Çekirdek & Devler (BİST 30)
            "AKBNK", "ARCLK", "ASELS", "BIMAS", "BRSAN", "CASA", "EKGYO", "ENKAI", 
            "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", 
            "KOZAL", "KRDMD", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", 
            "SISE", "TCELL", "THYAO", "TOASO", "TUPRS", "YKBNK",
            # Genişletilmiş BİST 50 & BİST 100 Hisseleri
            "AEFES", "AGHOL", "AHGAZ", "AKFYE", "AKSGY", "ALARK", "ALBRK", "ALFAS",
            "ANHYT", "ANSGR", "ASTOR", "BERA", "BIENP", "BOBET", "CANTE", "CIMSA",
            "CWENE", "DOAS", "DOHOL", "ECILC", "EGEEN", "ENJSA", "EUPWR", "GENIL",
            "GESAN", "GSDHO", "GWIND", "HALKB", "ISGYO", "IZMDC", "KARSN", "KAYSE",
            "KCAER", "KMPUR", "KONTR", "KORDS", "KOZAA", "MAVI", "MGROS", "MIATK",
            "PALEN", "QUAGR", "SDTTR", "SOKM", "SMRTG", "TABGD", "TAVHL", "TKFEN",
            "TMSN", "TSKB", "TTKOM", "ULKER", "VAKBN", "VESBE", "VESTL", "YEOTK",
            # Taze Halka Arzlar ve Dinamik Fırsatlar
            "GLRMK", "EFORC", "LILAK", "KOTON", "ENTRA"
        ]))

        rapor = f"""
📈🎯 *GALAKTİK BİST 100 NOKTA ATIŞI TARAMA RAPORU*
📅 *Tarih:* {tarih}
—
🟢 *SİSTEM:* BİST 30 / 50 / 100 TÜM HİSSELER TARANDI!

⭐ *ÇEKİRDEK PORTFÖY DURUMU:*
"""
        for kod in cekirdek_hisseler:
            fiyat, rsi, macd, degisim = get_live_macd_and_rsi(kod)
            if fiyat:
                yon = "🔺" if degisim >= 0 else "🔻"
                rapor += f"• *{kod}*: {fiyat:.2f} TL ({yon} %{degisim:.2f}) | RSI: {rsi} | MACD: {macd}\n"

        rapor += "\n🔥 *BİST 100 RADARINDAN YAKALANAN ALIM FIRSATLARI:* \n"
        firsat_bulundu_mu = False
        
        for kod in bist100_tarama_havuzu:
            # Çekirdek liderleri fırsat alanında tekrar basmamak için atla
            if kod in cekirdek_hisseler:
                continue
                
            fiyat, rsi, macd, degisim = get_live_macd_and_rsi(kod)
            
            if fiyat:
                # Sadece teknik kırılım yapan veya %3.5+ yükselen fırsatları cımbızlar
                if "GÜÇLÜ AL" in macd or degisim >= 3.5:
                    stop_fiyati = fiyat * 0.965
                    hedef_fiyat = fiyat * 1.080
                    yon = "🔺" if degisim >= 0 else "🔻"
                    
                    rapor += (
                        f"🚨 *{kod}* - {fiyat:.2f} TL ({yon} %{degisim:.2f})\n"
                        f"   ┣ 📥 *Alım Bölgesi:* {fiyat:.2f} TL\n"
                        f"   ┣ 🛑 *Stop-Loss (%3.5):* {stop_fiyati:.2f} TL\n"
                        f"   ┣ 💰 *Kâr Al Target (%8):* {hedef_fiyat:.2f} TL\n"
                        f"   ┗ 📊 RSI: {rsi} | MACD: {macd}\n\n"
                    )
                    firsat_bulundu_mu = True

        if not firsat_bulundu_mu:
            rapor += "ℹ️ BİST 100 genelinde şu an %3.5+ kırılım yapan veya Güçlü Al sinyali veren yeni hisse bulunamadı.\n"

        rapor += """
🚀 *SİSTEM DURUMU:*
• BİST 30, 50 ve 100 Hisseleri Taranmıştır
• Sadece Alım Şartı Sağlayan Hisseler Rapora Basılmıştır
"""
        return rapor.strip()
    except Exception as e:
        return f"⚠️ Rapor Hatası: {e}"

if __name__ == "__main__":
    bulten = generate_pure_bist_battle_report()
    send_telegram_message(bulten)
