
# v42 main uygulama dosyası
# "Tüm verileri sıfırla" artık yükleme geçmişini de temizleyecek.

def tum_verileri_sifirla():
    print("Veriler siliniyor...")
    # data klasörünü temizle
    import shutil, os
    if os.path.exists("data"):
        shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)

    # yükleme geçmişini temizle
    history_file = os.path.join("data", "upload_history.json")
    if os.path.exists(history_file):
        os.remove(history_file)
    print("Tüm veriler ve yükleme geçmişi sıfırlandı.")
