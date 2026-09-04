import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np

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

def calculate_rsi(data, window=14):
    """14 günlük RSI hesaplar."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data, window=20, num_std=2):
    """Bollinger Bantlarını hesaplar (Orta, Üst, Alt)."""
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean, upper_band, lower_band

def analyze_market_and_stocks():
    """
    Trend, Hacim, RSI ve Bollinger Bantları süzgeçlerine sahip 
    kurumsal düzeyde otonom karar mekanizması.
    """
    watchlist = [
        "KCHOL.IS", "THYAO.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS", "AKBNK.IS", 
        "ISCTR.IS", "EREGL.IS", "BIMAS.IS", "SAHOL.IS", "YKBNK.IS", "PGSUS.IS",
        "FROTO.IS", "TOASO.IS", "ARCLK.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", 
        "KRDMD.IS", "ENKAI.IS", "MGROS.IS", "TCELL.IS", "ODAS.IS", "KONTR.IS"
    ]
    
    report = "🎯 *KURUMSAL OTONOM STRATEJİ RAPORU*\n"
    report += "*(Trend + Hacim + RSI + Bollinger Süzgeci)*\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    actionable_signal_found = False
    
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            # Göstergelerin sağlıklı hesaplanması için yeterli geçmiş veri çekiyoruz (örn: 30 gün)
            hist = ticker.history(period="30d")
            
            if len(hist) < 20:
                continue
                
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            # 5 günlük trend değişimi
            five_day_start = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
            trend_change_5d = ((current_price - five_day_start) / five_day_start) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-2].mean()
            is_volume_spike = current_volume > (avg_volume * 1.2)
            
            # RSI Hesaplama
            rsi_series = calculate_rsi(hist['Close'])
            current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
            
            # Bollinger Bantları Hesaplama
            _, upper_band, lower_band = calculate_bollinger_bands(hist['Close'])
            curr_upper = upper_band.iloc[-1]
            is_above_upper_band = current_price > curr_upper
            
            report += f"🔹 *Hisse:* `{symbol}`\n"
            report += f"   • Fiyat: `{current_price:.2f} TL` (%{price_change:+.2f}) | RSI: `{current_rsi:.1f}`\n"
            
            # --- PROFESYONEL KARAR MATRİSİ ---
            # 1. AL Şartı: Trend pozitif (>0) AND Hacim var AND RSI aşırı alımda değil (<80) AND Bollinger üst bandını aşırı delmemiş.
            # 2. BEKLE/TUZAK: Trend negatif veya RSI çok şişmiş (>=80) veya Bollinger üstünde aşırı gerilmiş.
            
            if is_volume_spike and trend_change_5d > 0 and current_rsi < 80 and not is_above_upper_band:
                actionable_signal_found = True
                report += "   🟢 *KARAR: AL / GÜÇLÜ FIRSAT*\n"
                report += "   • 🚨 Trend onaylı, taze hacimli ve sağlıklı RSI seviyesi.\n"
                report += f"   • 🎯 *Strateji:* Giriş: `{current_price:.2f} TL` | Hedef: `+{float(current_price)*1.04:.2f} TL` | Stop-Loss: `{float(current_price)*0.98:.2f} TL`\n"
                report += "   • 💰 *Sermaye Kuralı:* Kasanın en fazla **%10-15**'i ayrılmalıdır.\n"
            elif current_rsi >= 80:
                report += "   🟡 *KARAR: BEKLE / AŞIRI ALIM (Tepe Riski)*\n"
                report += "   • ⚠️ *Uyarı:* RSI 80 sınırını aşarak aşırı şişmiş. Tepeden mal alma riski yüksek!\n"
            elif is_above_upper_band:
                report += "   🟡 *KARAR: BEKLE / BOLLINGER ÜST BANDI TAŞMASI*\n"
                report += "   • ⚠️ *Uyarı:* Fiyat bantların dışına çıkarak aşırı gerilmiş, düzeltme gelebilir.\n"
            elif is_volume_spike and trend_change_5d <= 0:
                report += "   🟡 *KARAR: BEKLE / TUZAK (Düşen Trend Tepkisi)*\n"
                report += "   • ⚠️ *Uyarı:* Hacim var ancak 5 günlük ana trend negatifte (Sasa tipi tuzak).\n"
            else:
                report += "   📊 *KARAR: İZLE / NÖTR*\n"
                report += "   • Güvenli bantta, belirgin bir ralli sinyali yok.\n"
                
            report += "------------------------------------\n"
            
        except Exception as e:
            print(f"{symbol} analizinde hata: {e}")
            
    if not actionable_signal_found:
        report += "\n📌 *Piyasa Özeti:* Tüm filtreler (Trend, Hacim, RSI, Bollinger) sıkıca uygulandı. Riskli veya tepe yapmış hareketler elendi, nakit disiplini korunuyor.\n"
        
    report += "\n💡 *Not:* Sadece çok katmanlı kurumsal süzgeçten geçen kusursuz sinyaller raporlanır."
    return report

if __name__ == "__main__":
    print("Çok katmanlı kurumsal bot çalıştırılıyor...")
    market_report = analyze_market_and_stocks()
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_message(market_report)
        print("Kurumsal strateji raporu Telegram'a başarıyla iletildi.")
    else:
        print("Telegram token veya chat ID eksik!")
