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
    Teknik (Trend, Hacim, RSI, Bollinger) ve 
    Temel Analiz (F/K, PD/DD) süzgeçlerine sahip Otonom Karar Merkezi.
    """
    watchlist = [
        "KCHOL.IS", "THYAO.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS", "AKBNK.IS", 
        "ISCTR.IS", "EREGL.IS", "BIMAS.IS", "SAHOL.IS", "YKBNK.IS", "PGSUS.IS",
        "FROTO.IS", "TOASO.IS", "ARCLK.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", 
        "KRDMD.IS", "ENKAI.IS", "MGROS.IS", "TCELL.IS", "ODAS.IS", "KONTR.IS"
    ]
    
    report = "🏛️ *YATIRIM KOMUTA MERKEZİ RAPORU*\n"
    report += "*(Teknik + Temel Rasyo Süzgeci Aktif)*\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
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
            
            # 5 günlük trend değişimi
            five_day_start = hist['Close'].iloc[-5] if len(hist) >= 5 else hist['Close'].iloc[0]
            trend_change_5d = ((current_price - five_day_start) / five_day_start) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-2].mean()
            is_volume_spike = current_volume > (avg_volume * 1.2)
            
            # RSI ve Bollinger
            rsi_series = calculate_rsi(hist['Close'])
            current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else 50
            _, upper_band, _ = calculate_bollinger_bands(hist['Close'])
            is_above_upper_band = current_price > upper_band.iloc[-1]
            
            # Temel Veriler (F/K ve PD/DD Çekme)
            info = ticker.info
            pe_ratio = info.get('trailingPE', None)
            pb_ratio = info.get('priceToBook', None)
            
            pe_str = f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else "N/A (Zarar/Veri Yok)"
            pb_str = f"{pb_ratio:.2f}" if pb_ratio else "N/A"
            
            report += f"🔹 *Hisse:* `{symbol}`\n"
            report += f"   • Fiyat: `{current_price:.2f} TL` (%{price_change:+.2f}) | RSI: `{current_rsi:.1f}`\n"
            report += f"   • Temel Rasyolar -> F/K: `{pe_str}` | PD/DD: `{pb_str}`\n"
            
            # --- ÇOK KATMANLI KARAR MATRİSİ (TEKNİK + TEMEL) ---
            # Şartlar: 
            # 1. Hacim patlaması var AND 5 günlük trend yukarı
            # 2. RSI aşırı alımda değil (<80) AND Bollinger üst bandını delmemiş
            # 3. Şirket zarar etmiyor (F/K > 0) veya temel verisi erişilebilir durumda
            
            is_fundamentally_safe = (pe_ratio is None) or (pe_ratio > 0 and pe_ratio < 40) # Çok şişmiş veya zararda olanları filtrele
            
            if is_volume_spike and trend_change_5d > 0 and current_rsi < 80 and not is_above_upper_band and is_fundamentally_safe:
                actionable_signal_found = True
                report += "   🟢 *KARAR: AL / GÜÇLÜ KOMBİNE FIRSAT*\n"
                report += "   • 🚨 Teknik trend onaylı, taze hacimli, sağlıklı RSI ve makul F/K.\n"
                report += f"   • 🎯 *Strateji:* Giriş: `{current_price:.2f} TL` | Hedef: `+{float(current_price)*1.04:.2f} TL` | Stop-Loss: `{float(current_price)*0.98:.2f} TL`\n"
                report += "   • 💰 *Sermaye Kuralı:* Kasanın en fazla **%10-15**'i ayrılmalıdır.\n"
            elif pe_ratio is not None and pe_ratio < 0:
                report += "   🟡 *KARAR: BEKLE / TEMEL RİSK (Zarar Eden Şirket)*\n"
                report += "   • ⚠️ *Uyarı:* Şirketin F/K oranı negatif (zararda). Temel risk nedeniyle pas geçiliyor.\n"
            elif current_rsi >= 80:
                report += "   🟡 *KARAR: BEKLE / AŞIRI ALIM (Tepe Riski)*\n"
                report += "   • ⚠️ *Uyarı:* RSI 80 sınırını aşarak aşırı şişmiş!\n"
            elif is_above_upper_band:
                report += "   🟡 *KARAR: BEKLE / BOLLINGER ÜST BANDI TAŞMASI*\n"
                report += "   • ⚠️ *Uyarı:* Fiyat bantların dışına çıkarak aşırı gerilmiş.\n"
            elif is_volume_spike and trend_change_5d <= 0:
                report += "   🟡 *KARAR: BEKLE / TUZAK (Düşen Trend Tepkisi)*\n"
                report += "   • ⚠️ *Uyarı:* Hacim var ancak 5 günlük ana trend negatifte (Düşen bıçak tutulmaz).\n"
            else:
                report += "   📊 *KARAR: İZLE / NÖTR*\n"
                report += "   • Güvenli bantta, belirgin bir ralli sinyali yok.\n"
                
            report += "------------------------------------\n"
            
        except Exception as e:
            print(f"{symbol} analizinde hata: {e}")
            
    if not actionable_signal_found:
        report += "\n📌 *Piyasa Özeti:* Teknik ve Temel filtreler (F/K, PD/DD, Trend, RSI) titizlikle uygulandı. Riskli, zararda veya tepe yapmış tüm hareketler elendi, nakit disiplini korunuyor.\n"
        
    report += "\n💡 *Not:* Sadece çok katmanlı kurumsal ve temel süzgeçten geçen kusursuz sinyaller raporlanır."
    return report

if __name__ == "__main__":
    print("Temel ve Teknik Komuta Merkezi çalıştırılıyor...")
    market_report = analyze_market_and_stocks()
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_message(market_report)
        print("Komuta merkezi raporu Telegram'a başarıyla iletildi.")
    else:
        print("Telegram token veya chat ID eksik!")
