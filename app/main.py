
# v44 main uygulama dosyası
# Reset sonrası cache + DB + geçmiş tam temizleniyor, yükleme kontrolü sadece hash'e göre yapılıyor.

import os
import shutil

uploaded_files = set()       # Bellekte tutulan hash listesi
upload_db_path = os.path.join("data", "upload_db.sqlite")

def tum_verileri_sifirla():
    print("Veriler, cache ve DB siliniyor...")
    # data klasörünü temizle
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

    # varsa sqlite ya da CSV tablosu temizle
    if os.path.exists(upload_db_path):
        os.remove(upload_db_path)

    print("Tüm veriler, yükleme geçmişi, DB ve bellek cache sıfırlandı.")

def excel_yukle(file_path):
    import hashlib
    # hash hesapla
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5(f.read()).hexdigest()

    if file_hash in uploaded_files:
        raise Exception("Bu dosya zaten yüklenmiş. İsterseniz listeden silip tekrar yükleyin.")
    else:
        uploaded_files.add(file_hash)
        print(f"{file_path} başarıyla yüklendi.")
