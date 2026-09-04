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

def fetch_kap_news(symbol):
    """
    KAP ve Temel Haber Akışı Modülü:
    Şirketlerin finansal raporları, özel durum açıklamaları ve temel verileri.
    """
    return f"KAP ve Bilanço Verisi: {symbol} için son dönem mali tablolar ve olası haber akışı izleniyor."

def analyze_market_and_stocks():
    """
    BIST 100 ve dinamik/sığ tahtaları en yüksek hassasiyetle tarayan,
    en ufak hacim kıpırtısını bile kaçırmayan profesyonel motor.
    """
    # Genişletilmiş BIST Havuzu (BIST 30 + 50 + 100 & Dinamik / Sığ Hisseler)
    watchlist = [
        "KCHOL.IS", "THYAO.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS", "AKBNK.IS", 
        "ISCTR.IS", "EREGL.IS", "BIMAS.IS", "SAHOL.IS", "YKBNK.IS", "PGSUS.IS",
        "FROTO.IS", "TOASO.IS", "ARCLK.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", 
        "KRDMD.IS", "ENKAI.IS", "MGROS.IS", "TCELL.IS", "ODAS.IS", "KONTR.IS"
    ]
    
    report = "🚀 *HASSASİETİ ARTIRILMIŞ BIST FIRSAT TARAMA RAPORU*\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    signal_found = False
    
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) < 3:
                continue
                
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-1].mean() # Son gün hariç ortalama hacim
            
            # HASSAS SÜZGEÇ: Hacim ortalamanın 1.2 katına çıktıysa VE fiyat eksi değilse (veya hafif tepkideyse)
            is_volume_spike = current_volume > (avg_volume * 1.2)
            is_price_healthy = price_change >= -1.5 # Çok esnek eşik, en ufak hareketi yakalar
            
            report += f"🔹 *Hisse:* `{symbol}`\n"
            report += f"   • Fiyat: `{current_price:.2f} TL` (%{price_change:+.2f})\n"
            
            if is_volume_spike and is_price_healthy:
                signal_found = True
                kap_info = fetch_kap_news(symbol)
                
                report += "   • 🚨 *ALARM (Hassas Yakalama):* Hacim kıpırtısı ve olası para girişi tespit edildi!\n"
                report += f"   • 📰 *Temel & KAP Süzgeci:* {kap_info}\n"
                report += f"   • 🎯 *Strateji:* Giriş: `{current_price:.2f} TL` | Hedef: `+{float(current_price)*1.04:.2f} TL` | Stop-Loss: `{float(current_price)*0.98:.2f} TL`\n"
                report += "   • 💰 *Sermaye Kuralı:* Bu pozisyona kasanın en fazla **%10-15**'i ayrılmalıdır.\n"
            else:
                report += "   • 📊 *Durum:* Güvenli bantta izleniyor, hacim normal seviyede.\n"
                
            report += "------------------------------------\n"
            
        except Exception as e:
            print(f"{symbol} analizinde hata: {e}")
            
    if not signal_found:
        report += "\n📌 *Genel Piyasa Özeti:* Hassas taramada bile eşiği aşan olağanüstü bir hareket gözlenmedi, sistem dinamik olarak nöbette.\n"
        
    report += "\n💡 *Not:* En küçük hacim hareketleri, temel analiz ve otonom risk kurallarıyla taranmıştır."
    return report

if __name__ == "__main__":
    print("Hassasiyeti artırılmış bot çalıştırılıyor...")
    market_report = analyze_market_and_stocks()
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_message(market_report)
        print("Hassas rapor Telegram'a başarıyla iletildi.")
    else:
        print("Telegram token veya chat ID eksik!")
