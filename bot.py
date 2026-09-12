import os
import subprocess
import sys

# Sigorta Mekanizması: Ortamda eksik paket varsa anında otomatik kurar
for package in ["requests", "yfinance", "pandas", "numpy", "pandas-ta"]:
    try:
        __import__(package.replace("-ta", "_ta"))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import requests
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Telegram Ayarları (GitHub Secrets'tan otomatik alınır)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram kimlik bilgileri eksik!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def analyze_stock(ticker_symbol):
    try:
        df = yf.download(ticker_symbol, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 30:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Profesyonel İndikatörler (pandas-ta)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        macd = ta.macd(df['Close'])
        if macd is not None and not macd.empty:
            df['MACD'] = macd.iloc[:, 0]
        else:
            df['MACD'] = 0

        st = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
        if st is not None and not st.empty:
            st_dir_col = [c for c in st.columns if 'SUPERTd_' in c]
            supertrend_dir = st[st_dir_col[0]].iloc[-1] if st_dir_col else 1
        else:
            supertrend_dir = 1

        last = df.iloc[-1]
        
        # Hacim Analizi
        vol_sma = df['Volume'].rolling(window=20).mean().iloc[-1]
        is_volume_spike = last['Volume'] > (1.5 * vol_sma) if vol_sma > 0 else False

        return {
            "close": float(last['Close']),
            "rsi": round(float(last['RSI']), 2) if not pd.isna(last['RSI']) else 0,
            "supertrend_signal": "AL (Yeşil)" if supertrend_dir == 1 else "SAT (Kırmızı)",
            "volume_spike": is_volume_spike
        }
    except Exception as e:
        print(f"{ticker_symbol} analiz hatası: {e}")
        return None

def run_daily_bot():
    core_stocks = ["THYAO.IS", "ASELS.IS", "KCHOL.IS", "TUPRS.IS", "BIMAS.IS"]
    
    report = "🚀 *GÜNLÜK PROFESYONEL TARAMA RAPORU* 🚀\n"
    report += "----------------------------------------\n"
    
    for stock in core_stocks:
        res = analyze_stock(stock)
        short_name = stock.replace(".IS", "")
        if res:
            vol_str = "🔥 Hacim Patlaması" if res["volume_spike"] else "Sakin"
            report += f"• `{short_name}` | Fiyat: {res['close']:.2f} | RSI: {res['rsi']} | ST: {res['supertrend_signal']} | {vol_str}\n"
        else:
            report += f"• `{short_name}` | Veri bekleniyor...\n"

    report += "\n🎯 *Sistem Mühürlendi ve Hazır.*"
    send_telegram_message(report)

if __name__ == "__main__":
    run_daily_bot()
