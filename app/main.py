
# v43 main uygulama dosyası
# Reset sonrası bellek cache + yükleme geçmişi de temizlenecek

uploaded_files = set()  # Bellekte tutulan hash listesi

def tum_verileri_sifirla():
    print("Veriler ve cache siliniyor...")
    # data klasörünü temizle
    import shutil, os
    if os.path.exists("data"):
        shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)

    # yükleme geçmişini temizle
    history_file = os.path.join("data", "upload_history.json")
    if os.path.exists(history_file):
        os.remove(history_file)

    # Bellekteki hash/cache sıfırla
    global uploaded_files
    uploaded_files.clear()
    print("Tüm veriler, yükleme geçmişi ve bellek cache sıfırlandı.")
