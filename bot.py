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
    """Bollinger Bantlarını hesaplar."""
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return rolling_mean, upper_band, lower_band

def get_macro_and_asset_allocation_advice():
    """Makroekonomik görünüm ve çoklu varlık (Altın, Fon, Kripto, Hisse) strateji önerisi üretir."""
    advice = "🌐 *MAKRO & VARLIK DAĞILIMI STRATEJİSİ*\n"
    advice += "• *Altın / Güvenli Liman:* Enflasyonist baskılar ve küresel dalgalanmalarda portföyün çekirdek koruması olarak kademeli tutulmalıdır.\n"
    advice += "• *Yatırım / Katılım Fonları:* Tekil risklerden kaçınmak ve profesyonel yönetimden faydalanmak için likit/kira sertifikası ve sepet fonlar dengede tutulmalıdır.\n"
    advice += "• *Kripto Varlıklar:* Yüksek volatilite barındırdığı için toplam portföyün yalnızca risk atılabilir küçük bir bölümüyle (kademeli) takip edilmelidir.\n"
    advice += "• *BIST Hisse Senedi:* Sadece temel ve teknik süzgeçten geçen, bilançosu güçlü şirketlerde seçici olunmalıdır.\n"
    advice += "------------------------------------\n"
    return advice

def analyze_market_and_stocks():
    """
    Teknik + Temel + Makro & Varlık Dağılımı Entegre Komuta Merkezi.
    """
    watchlist = [
        "KCHOL.IS", "THYAO.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS", "AKBNK.IS", 
        "ISCTR.IS", "EREGL.IS", "BIMAS.IS", "SAHOL.IS", "YKBNK.IS", "PGSUS.IS",
        "FROTO.IS", "TOASO.IS", "ARCLK.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", 
        "KRDMD.IS", "ENKAI.IS", "MGROS.IS", "TCELL.IS", "ODAS.IS", "KONTR.IS"
    ]
    
    report = "🏛️ *YATIRIM KOMUTA MERKEZİ RAPORU*\n"
    report += "*(Teknik + Temel Rasyo + Makro Varlık Dağılımı Aktif)*\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Makro ve Varlık Dağılım Tavsiyesini Rapora Ekleyelim
    report += get_macro_and_asset_allocation_advice() + "\n"
    report += "📊 *BIST 30/100 SEÇİCİ TARAMA SONUÇLARI:*\n\n"
    
    actionable_signal_found = False
    
    for symbol in watchlist:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="30d")
            
            if len(hist) < 20:
                continue
                
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            five_day_start = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
            trend_change_5d = ((current_price - five_day_start) / five_day_start) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-2].mean()
            is_volume_spike = current_volume > (avg_volume * 1.2)
            
            rsi_series = calculate_rsi(hist['Close'])
            current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
            _, upper_band, _ = calculate_bollinger_bands(hist['Close'])
            is_above_upper_band = current_price > upper_band.iloc[-1]
            
            info = ticker.info
            pe_ratio = info.get('trailingPE', None)
            pb_ratio = info.get('priceToBook', None)
            
            pe_str = f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A (Zarar/Veri Yok)"
            pb_str = f"{pb_ratio:.2f}" if pb_ratio else "N/A"
            
            report += f"🔹 *Hisse:* `{symbol}`\n"
            report += f"   • Fiyat: `{current_price:.2f} TL` (%{price_change:+.2f}) | RSI: `{current_rsi:.1f}`\n"
            report += f"   • Rasyolar -> F/K: `{pe_str}` | PD/DD: `{pb_str}`\n"
            
            is_fundamentally_safe = (pe_ratio is None) or (pe_ratio > 0 and pe_ratio < 40)
            
            if is_volume_spike and trend_change_5d > 0 and current_rsi < 80 and not is_above_upper_band and is_fundamentally_safe:
                actionable_signal_found = True
                report += "   🟢 *KARAR: AL / GÜÇLÜ KOMBİNE FIRSAT*\n"
                report += "   • 🚨 Teknik trend onaylı, taze hacimli, sağlıklı RSI ve makul F/K.\n"
                report += f"   • 🎯 *Stratejik Çerçeve:* Takip Bölgesi: `{current_price:.2f} TL` | Hedef Bölge: `+{float(current_price)*1.04:.2f} TL` | Stop-Loss: `{float(current_price)*0.98:.2f} TL`\n"
                report += "   • 💰 *Sermaye Disiplini:* Portföyün en fazla **%10-15**'i tahsis edilmelidir.\n"
            elif pe_ratio is not None and pe_ratio < 0:
                report += "   🟡 *KARAR: BEKLE / TEMEL RİSK (Zarar Eden Şirket)*\n"
            elif current_rsi >= 80:
                report += "   🟡 *KARAR: BEKLE / AŞIRI ALIM (Tepe Riski)*\n"
            elif is_above_upper_band:
                report += "   🟡 *KARAR: BEKLE / BOLLINGER ÜST BANDI TAŞMASI*\n"
            elif is_volume_spike and trend_change_5d <= 0:
                report += "   🟡 *KARAR: BEKLE / TUZAK (Düşen Trend Tepkisi)*\n"
            else:
                report += "   📊 *KARAR: İZLE / NÖTR*\n"
                
            report += "------------------------------------\n"
            
        except Exception as e:
            print(f"{symbol} analizinde hata: {e}")
            
    if not actionable_signal_found:
        report += "\n📌 *Piyasa Özeti:* Çok katmanlı tarama sonucunda net tetikleyici koşul oluşmadı. Sermaye koruma ve nakit disiplini prensibiyle sistem sessizliğini koruyor.\n"
        
    report += "\n💡 *Not:* Bu rapor yatırım tavsiyesi değil; yapay zeka destekli istatistiksel bir karar destek ve varlık dağılım rehberidir."
    return report

if __name__ == "__main__":
    print("Tam Donanımlı Yatırım Komuta Merkezi çalıştırılıyor...")
    market_report = analyze_market_and_stocks()
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_message(market_report)
        print("Komuta merkezi raporu Telegram'a başarıyla iletildi.")
    else:
        print("Telegram token veya chat ID eksik!")
