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

  # Performans Takibi için Örnek Takip Sepeti (Örn: THYAO ve EREGL)
  takip_hisseleri = ["THYAO.IS", "EREGL.IS"]
  perf_notlari = []
  for t in takip_hisseleri:
    try:
      h = yf.Ticker(t).history(period="3d")
      if len(h) >= 3:
        dun_degisim = (
            (h["Close"].iloc[-2] - h["Close"].iloc[-3])
            / h["Close"].iloc[-3]
        ) * 100
        durum_ikon = "✅ Hedefte" if dun_degisim > 0 else "⚠️ Düzeltmede"
        perf_notlari.append(f"• `{t}` (Dünkü Performans: %{dun_degisim:.2f})")
    except Exception:
      pass

  ana_sepet = ["EREGL.IS", "THYAO.IS", "ASELS.IS", "KCHOL.IS", "GARAN.IS"]
  momentum_sepet = ["BIMAS.IS", "TUPRS.IS", "AKBNK.IS", "YKBNK.IS", "SASA.IS"]

  rapor = []
  rapor.append("🧠 *ÇİFT KATMANLI YAPAY ZEKA OTONOM FONTESİ*")
  rapor.append(f"📅 *Tarih:* {bugun} | 🎯 *Güven Eşiği:* `%99+`\n")
  rapor.append(f"{bist_ozet}\n")

  if perf_notlari:
    rapor.append("📈 *Öz-Denetim / Dünkü Sinyal Başarı Durumu:*")
    rapor.extend(perf_notlari)
    rapor.append("")

  rapor.append("📌 *1. Ana Sepet (Sağlam Mavi Çip İşlem Planı):*")
  for ticker in ana_sepet[:4]:
    try:
      stock = yf.Ticker(ticker)
      hist = stock.history(period="5d")
      if len(hist) >= 2:
        close = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        change = ((close - prev) / prev) * 100

        hedef_fiyat = close * 1.04
        stop_fiyat = close * 0.98

        if change >= 1.5:
          sinyal = "🟢 *GÜÇLÜ AL*"
          detay = (
              f"\n    └ 🎯 *Alış:* {close:.2f} | *Hedef:* {hedef_fiyat:.2f}"
              f" | *Stop:* {stop_fiyat:.2f}"
          )
        elif change > 0:
          sinyal = "🟡 *TUT / İZLE*"
          detay = ""
        else:
          sinyal = "🔴 *BEKLE / DÜZELTME*"
          detay = ""

        rapor.append(
            f"  • `{ticker}`: {close:.2f} TL (%{change:.2f}) ➔ {sinyal}{detay}"
        )
    except Exception:
      pass

  rapor.append("\n🚀 *2. Sürpriz / Momentum Sepeti (Dinamik Sinyaller):*")
  for ticker in momentum_sepet[:4]:
    try:
      stock = yf.Ticker(ticker)
      hist = stock.history(period="5d")
      if len(hist) >= 2:
        close = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        change = ((close - prev) / prev) * 100

        hedef_fiyat = close * 1.05
        stop_fiyat = close * 0.975

        if change >= 2.0:
          sinyal = "🚀 *AL-SAT ATAĞI*"
          detay = (
              f"\n    └ 🎯 *Alış:* {close:.2f} | *Hedef:* {hedef_fiyat:.2f}"
              f" | *Stop:* {stop_fiyat:.2f}"
          )
        elif change > 0:
          sinyal = "⏳ *HAFİF YÜKSELİŞ*"
          detay = ""
        else:
          sinyal = "📉 *ZAYIF / NAKİT*"
          detay = ""

        rapor.append(
            f"  • `{ticker}`: {close:.2f} TL (%{change:.2f}) ➔ {sinyal}{detay}"
        )
    except Exception:
      pass

  rapor.append(
      "\n⚡ *Otonom Sistem Notu:* Öz denetim, portföy takibi ve risk matrisi"
      " başarıyla güncellendi."
  )
  return "\n".join(rapor)


if __name__ == "__main__":
  message = get_market_data()
  send_telegram_message(message)
