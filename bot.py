import os
import requests
import yfinance as yf

# Telegram Ayarları (GitHub Secrets üzerinden otomatik çekilir)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Telegram üzerinden bildirim gönderir."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def analyze_market_and_stocks():
    """Genişletilmiş havuzu ve risk kurallarını yönetir."""
    watchlist = [
        "KCHOL.IS",
        "THYAO.IS",
        "ASELS.IS",
        "TUPRS.IS",
        "GARAN.IS",
        "BIMAS.IS"
    ]
    
    report = "🚀 *PROFESYONEL BIST & FIRSAT TARAMA RAPORU*\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) < 2:
                continue
                
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            is_volume_spike = current_volume > (avg_volume * 1.5)
            
            report += f"🔹 *Hisse:* `{symbol}`\n"
            report += f"   • Fiyat: `{current_price:.2f} TL` (%{price_change:+.2f})\n"
            
            if is_volume_spike:
                report += "   • 🚨 *ALARM:* Hacim patlaması ve para girişi tespit edildi!\n"
                report += f"   • 🎯 *Önerilen Strateji:* Giriş: `{current_price:.2f} TL` | Hedef: `+{float(current_price)*1.04:.2f} TL` | Stop-Loss: `{float(current_price)*0.98:.2f} TL`\n"
                report += "   • 💰 *Sermaye Kuralı:* Bu pozisyona kasanın en fazla **%10-15**'ini ayırın.\n"
            else:
                report += "   • 📊 *Durum:* Sakin seyir, yatay bant izleniyor. Beklemede.\n"
                
            report += "------------------------------------\n"
            
        except Exception as e:
            print(f"{symbol} analitiğinde hata: {e}")
            
    report += "\n💡 *Not:* Güncel veriler ve risk kuralları otonom olarak işlenmiştir."
    return report

if __name__ == "__main__":
    print("Bot çalıştırılıyor...")
    market_report = analyze_market_and_stocks()
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_message(market_report)
        print("Rapor Telegram'a başarıyla gönderildi.")
    else:
        print("Telegram token veya chat ID eksik!")
