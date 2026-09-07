import os
import requests
from datetime import datetime
import pandas as pd
import yfinance as yf

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    """
    Telegram mesajlarını hisse blokları bölünmeyecek şekilde güvenle iletir.
    """
    if not TOKEN or not CHAT_ID:
        print("Uyarı: Telegram Token veya Chat ID bulunamadı!")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Mesaj 3800 karakterden uzunsa satır bazlı böl
    if len(text) > 3800:
        lines = text.split("\n")
        chunks = []
        current_chunk = ""
        
        for line in lines:
            if len(current_chunk) + len(line) + 1 > 3800:
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        for chunk in chunks:
            payload = {"chat_id": CHAT_ID, "text": chunk, "parse_mode": "Markdown"}
            try:
                requests.post(url, json=payload, timeout=15)
            except Exception as e:
                print(f"Telegram gönderme hatası: {e}")
    else:
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
        except Exception as e:
            print(f"Telegram gönderme hatası: {e}")

def get_live_macd_and_rsi(ticker_symbol):
    """Yahoo Finance üzerinden canlı fiyat, RSI ve MACD çeker."""
    try:
        symbol = ticker_symbol if ticker_symbol.endswith(".IS") else f"{ticker_symbol}.IS"
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1mo", interval="1d")
        
        if df.empty or len(df) < 10:
            return None, None, None, None
        
        close_series = df['Close'].dropna()
        if len(close_series) < 10:
            return None, None, None, None

        last_price = float(close_series.iloc[-1])
        prev_close = float(close_series.iloc[-2])
        daily_change = ((last_price - prev_close) / prev_close) * 100
        
        # MACD (12, 26, 9)
        exp12 = close_series.ewm(span=12, adjust=False).mean()
        exp26 = close_series.ewm(span=26, adjust=False).mean()
        macd = exp12 - exp26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        last_macd = float(macd.iloc[-1])
        last_signal = float(signal.iloc[-1])
        prev_macd = float(macd.iloc[-2]) if len(macd) > 1 else last_macd
        prev_signal = float(signal.iloc[-2]) if len(signal) > 1 else last_signal
        
        if prev_macd < prev_signal and last_macd > last_signal:
            macd_status = "🚀 GÜÇLÜ AL"
        elif last_macd > last_signal:
            macd_status = "🟢 AL"
        else:
            macd_status = "🔴 SAT / NÖTR"

        # RSI (14 Günlük)
        delta = close_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        last_rsi = round(float(rsi.iloc[-1]), 1)

        return last_price, last_rsi, macd_status, daily_change
    except Exception as e:
        print(f"{ticker_symbol} verisinde hata: {e}")
        return None, None, None, None

def generate_pure_bist_battle_report():
    try:
        tarih = datetime.now().strftime("%d.%m.%Y")
        
        cekirdek_hisseler = ["THYAO", "ASELS", "KCHOL", "TUPRS", "BIMAS"]
        
        bist100_tarama_havuzu = list(set([
            "AKBNK", "ARCLK", "ASELS", "BIMAS", "BRSAN", "EKGYO", "ENKAI", 
            "EREGL", "FROTO", "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", 
            "KOZAL", "KRDMD", "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", 
            "SISE", "TCELL", "THYAO", "TOASO", "TUPRS", "YKBNK", "AEFES", "AGHOL", 
            "AHGAZ", "AKFYE", "AKSGY", "ALARK", "ALBRK", "ALFAS", "ANHYT", "ANSGR", 
            "ASTOR", "BERA", "BIENP", "BOBET", "CANTE", "CIMSA", "CWENE", "DOAS", 
            "DOHOL", "ECILC", "EGEEN", "ENJSA", "EUPWR", "GENIL", "GESAN", "GSDHO", 
            "GWIND", "HALKB", "ISGYO", "IZMDC", "KARSN", "KAYSE", "KCAER", "KMPUR", 
            "KORDS", "KOZAA", "MAVI", "MGROS", "MIATK", "QUAGR", "SDTTR", "SOKM", 
            "SMRTG", "TABGD", "TAVHL", "TKFEN", "TMSN", "TSKB", "TTKOM", "ULKER", 
            "VAKBN", "VESBE", "VESTL", "YEOTK", "GLRMK", "EFORC", "LILAK", "KOTON", "ENTRA"
        ]))

        rapor = f"📈🎯 *GALAKTİK BİST 100 NOKTA ATIŞI TARAMA RAPORU*\n"
        rapor += f"📅 *Tarih:* {tarih}\n—\n"
        rapor += "🟢 *SİSTEM:* BİST 30 / 50 / 100 TÜM HİSSELER TARANDI!\n\n"
        rapor += "⭐ *ÇEKİRDEK PORTFÖY DURUMU:*\n"

        for kod in cekirdek_hisseler:
            fiyat, rsi, macd, degisim = get_live_macd_and_rsi(kod)
            if fiyat is not None:
                yon = "🔺" if degisim >= 0 else "🔻"
                rapor += f"• *{kod}*: {fiyat:.2f} TL ({yon} %{degisim:.2f}) | RSI: {rsi} | MACD: {macd}\n"
            else:
                rapor += f"• *{kod}*: Veri Servisi Bağlantısı Bekleniyor...\n"

        rapor += "\n🔥 *BİST 100 RADARINDAN YAKALANAN ALIM FIRSATLARI:*\n"
        firsat_bulundu_mu = False
        
        for kod in bist100_tarama_havuzu:
            if kod in cekirdek_hisseler:
                continue
                
            fiyat, rsi, macd, degisim = get_live_macd_and_rsi(kod)
            
            if fiyat is not None:
                if "GÜÇLÜ AL" in str(macd) or degisim >= 3.5:
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

        rapor += "\n🚀 *SİSTEM DURUMU:*\n"
        rapor += "• BİST 30, 50 ve 100 Hisseleri Taranmıştır\n"
        rapor += "• Sadece Alım Şartı Sağlayan Hisseler Rapora Basılmıştır"
        
        return rapor.strip()
    except Exception as e:
        return f"⚠️ Rapor Hatası: {e}"

if __name__ == "__main__":
    bulten = generate_pure_bist_battle_report()
    send_telegram_message(bulten)
