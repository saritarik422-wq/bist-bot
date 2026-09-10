import pandas as pd
import yfinance as yf

# Takip listemizdeki skalp hisseleri
HISSE_LISTESI = ["BERA.IS", "BOBET.IS", "VESBE.IS", "ODAS.IS", "ALBRK.IS"]

def rsi_hesapla(veri, periyot=7):
    # Hızlı skalp için RSI-7 hesaplaması
    delta = veri['Close'].diff()
    kazanc = (delta.where(delta > 0, 0)).rolling(window=periyot).mean()
    kayip = (-delta.where(delta < 0, 0)).rolling(window=periyot).mean()
    rs = kazanc / kayip
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi7_taramasi():
    print("--- 2 ve 3 Artan Fırsat Botu (RSI-7 Skalp) Çalıştı ---")
    
    for hisse in HISSE_LISTESI:
        try:
            df = yf.download(hisse, period="5d", interval="15m", progress=False)
            if df.empty:
                continue
                
            df['RSI_7'] = rsi_hesapla(df, periyot=7)
            son_rsi = df['RSI_7'].iloc[-1]
            son_fiyat = df['Close'].iloc[-1]
            
            print(f"Hisse: {hisse} | Fiyat: {son_fiyat:.2f} | RSI-7: {son_rsi:.2f}")
            
            # Tetik seviyeleri kontrolü
            if 30 <= son_rsi <= 40:
                print(f"-> [DIP DÖNÜŞÜ] {hisse} dip bölgesinde kıvrılıyor! RSI-7: {son_rsi:.2f}")
            elif son_rsi > 50:
                print(f"-> [MOMENTUM] {hisse} yukarı yönlü hareketini sürdürüyor. RSI-7: {son_rsi:.2f}")
            elif son_rsi >= 80:
                print(f"-> [AŞIRI ALIM / SAT] {hisse} tepe bölgede, kâr alıp çıkmaya uygun! RSI-7: {son_rsi:.2f}")
                
        except Exception as e:
            print(f"{hisse} taranırken hata oluştu: {e}")

if __name__ == "__main__":
    rsi7_taramasi()
