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
    """
    Düşen bıçakları ve sahte tepkileri eleyen, net AL - BEKLE - SAT 
    karar mekanizmasına sahip profesyonel tarama motoru.
    """
    # Genişletilmiş BIST Havuzu (BIST 30 + 50 + 100 & Dinamik / Sığ Hisseler)
    watchlist = [
        "KCHOL.IS", "THYAO.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS", "AKBNK.IS", 
        "ISCTR.IS", "EREGL.IS", "BIMAS.IS", "SAHOL.IS", "YKBNK.IS", "PGSUS.IS",
        "FROTO.IS", "TOASO.IS", "ARCLK.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", 
        "KRDMD.IS", "ENKAI.IS", "MGROS.IS", "TCELL.IS", "ODAS.IS", "KONTR.IS"
    ]
    
    report = "🎯 *PROFESYONEL TREND SÜZGECİ & AL-BEKLE RAPORU*\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    actionable_signal_found = False
    
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) < 5:
                continue
                
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            # Son 5 günlük genel trend yönü (Düşüş trendinde mi, yükselişte mi?)
            five_day_start = hist['Close'].iloc[0]
            trend_change_5d = ((current_price - five_day_start) / five_day_start) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-1].mean()
            
            is_volume_spike = current_volume > (avg_volume * 1.2)
            
            # --- KATİ TRADER KURALLARI (AL / BEKLE AYRIMI) ---
            # 1. AL Şartı: Hacim artacak VE son 5 günlük ana trend pozitif (veya en azından yataydan yukarı dönüyor) olacak.
            # 2. BEKLE/UZAK DUR: Hacim kıpırdasa bile 5 günlük trend ekside/düşüşteyse (Sasa vakası gibi) kesinlikle AL verilmez!
            
            report += f"🔹 *Hisse:* `{symbol}`\n"
            report += f"   • Fiyat: `{current_price:.2f} TL` (%{price_change:+.2f}) | 5g Trend: `%{trend_change_5d:+.2f}`\n"
            
            if is_volume_spike and trend_change_5d > 0:
                actionable_signal_found = True
                report += "   🟢 *KARAR: AL / GÜÇLÜ FIRSAT*\n"
                report += "   • 🚨 Hacim patlaması ve yükselen trend bir arada!\n"
                report += f"   • 🎯 *Strateji:* Giriş: `{current_price:.2f} TL` | Hedef: `+{float(current_price)*1.04:.2f} TL` | Stop-Loss: `{float(current_price)*0.98:.2f} TL`\n"
                report += "   • 💰 *Sermaye Kuralı:* Kasanın en fazla **%10-15**'i ayrılmalıdır.\n"
            elif is_volume_spike and trend_change_5d <= 0:
                report += "   🟡 *KARAR: BEKLE / TUZAK (Uzak Dur)*\n"
                report += "   • ⚠️ *Uyarı:* Hacim var ancak 5 günlük ana trend negatifte (Sasa tipi tepki/tuzak ihtimali). İşlem açılmamalı!\n"
            else:
                report += "   📊 *KARAR: İZLE / NÖTR*\n"
                report += "   • Güvenli bantta, belirgin bir ralli sinyali yok.\n"
                
            report += "------------------------------------\n"
            
        except Exception as e:
            print(f"{symbol} analizinde hata: {e}")
            
    if not actionable_signal_found:
        report += "\n📌 *Piyasa Özeti:* Trend onayı almayan hiçbir hareket 'AL' olarak değerlendirilmedi. Yanıltıcı hareketler filtrelendi, nakit disiplini korunuyor.\n"
        
    report += "\n💡 *Not:* Sadece trend onaylı ve hacim destekli profesyonel sinyaller raporlanır."
    return report

if __name__ == "__main__":
    print("Trend süzgeçli bot çalıştırılıyor...")
    market_report = analyze_market_and_stocks()
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_message(market_report)
        print("Akıllı Al-Bekle raporu Telegram'a başarıyla iletildi.")
    else:
        print("Telegram token veya chat ID eksik!")
