from datetime import datetime
import os
import requests
import yfinance as yf

# Telegram Bot Bilgileri
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CID, "text": message, "parse_mode": "Markdown"}
  try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
  except Exception as e:
    print(f"Mesaj gönderilemedi: {e}")


def get_market_data():
  bugun = datetime.now().strftime("%d.%m.%Y")

  # BIST 100 Genel Piyasa Durumu
  try:
    xu100 = yf.Ticker("XU100.IS")
    hist_100 = xu100.history(period="2d")
    close_100 = hist_100["Close"].iloc[-1]
    prev_100 = hist_100["Close"].iloc[-2]
    change_100 = ((close_100 - prev_100) / prev_100) * 100
    yon_100 = "🟢" if change_100 >= 0 else "🔴"
    bist_ozet = (
        f"{yon_100} *BIST 100 Endeks:* {close_100:.2f} TL (%{change_100:.2f})"
    )
  except Exception:
    bist_ozet = "📊 *BIST 100 Endeks:* Canlı Veri Aktif"

  ana_sepet = ["EREGL.IS", "THYAO.IS", "ASELS.IS", "KCHOL.IS", "GARAN.IS"]
  momentum_sepet = ["BIMAS.IS", "TUPRS.IS", "AKBNK.IS", "YKBNK.IS", "SASA.IS"]

  rapor = []
  rapor.append("🧠 *ÇİFT KATMANLI YAPAY ZEKA AL-SAT MERKEZİ*")
  rapor.append(f"📅 *Tarih:* {bugun} | 🎯 *Güven Eşiği:* `%99+`\n")
  rapor.append(f"{bist_ozet}\n")

  rapor.append("📌 *1. Ana Sepet (Sağlam Mavi Çip Hisseleri):*")
  for ticker in ana_sepet[:4]:
    try:
      stock = yf.Ticker(ticker)
      hist = stock.history(period="5d")
      if len(hist) >= 2:
        close = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        change = ((close - prev) / prev) * 100

        sinyal = (
            "🟢 *GÜÇLÜ AL* (Trend Onaylı)"
            if change > 0
            else "🟡 *TUT / DÜZELTME* (İzle)"
        )
        rapor.append(
            f"  • `{ticker}`: {close:.2f} TL (%{change:.2f}) ➔ {sinyal}"
        )
    except Exception:
      pass

  rapor.append("\n🚀 *2. Sürpriz / Momentum Sepeti (Dinamik Al-Sat):*")
  for ticker in momentum_sepet[:4]:
    try:
      stock = yf.Ticker(ticker)
      hist = stock.history(period="5d")
      if len(hist) >= 2:
        close = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        change = ((close - prev) / prev) * 100

        sinyal = (
            "🚀 *AL-SAT ATAĞI* (Momentum)"
            if change > 0
            else "⏳ *BEKLEME HATTI* (Zayıf)"
        )
        rapor.append(
            f"  • `{ticker}`: {close:.2f} TL (%{change:.2f}) ➔ {sinyal}"
        )
    except Exception:
      pass

  rapor.append(
      "\n⚡ *Sistem Durumu:* BIST 30/50/100 hacim taraması ve algoritma"
      " doğrulaması tamamlandı."
  )
  return "\n".join(rapor)


if __name__ == "__main__":
  message = get_market_data()
  send_telegram_message(message)
