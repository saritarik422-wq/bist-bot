import os
import requests
import yfinance as yf

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")



def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Mesaj gönderilemedi: {e}")
def check_bist():
    tickers = ["EREGL.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "KCHOL.IS", "TUPRS.IS"]
    report = "📊 *BIST Günlük Volatilite ve Fiyat Raporu*\n\n"
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change = ((current_price - prev_price) / prev_price) * 100
                report += f"🔹 *{ticker.replace('.IS', '')}*: {current_price:.2f} TL (%{change:+.2f})\n"
        except Exception as e:
            print(f"{ticker} alınamadı: {e}")
            
    send_telegram_message(report)
if __name__ == "__main__":
    check_bist()

