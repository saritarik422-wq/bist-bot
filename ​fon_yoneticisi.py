# Fortress Fon Yoneticisi ve Alpha-Prime Modulu
# Sabit Fon Listesi (Muhurlenen Sepet)
STABLE_FUNDS = ["KPC", "KTM", "KTV", "KCV", "KZL"]
GROWTH_FUNDS = ["KTJ", "KNJ", "TVE", "KGM"]

def fon_karar_mekanizmasi(bist100_fiyat, sma_50):
    """
    BIST100 ve SMA50 degerine gore guvenli mod veya buyume modunu belirler.
    """
    if bist100_fiyat > sma_50:
        return (
            "🟢 YESIL ISIK YANDI (Atilim Zamani)\n"
            f"Guvenli Fonlar ({', '.join(STABLE_FUNDS)})\n"
            f"Bulusma Noktasi ve Buyume Fonlari ({', '.join(GROWTH_FUNDS)}) aktif dagilim."
        )
    else:
        return (
            "🔴 KIRMIZI ISIK / GUVENLI MOD\n"
            f"Risk almiyoruz. Birikimler guvenli liman olan KTV ve KCV fonlarina yonlendiriliyor."
        )
