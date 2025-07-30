
# v45 main uygulama dosyası
# Yüklenmiş dosya kontrolü kaldırıldı, tekrar yükleme serbest.

import os
import shutil

uploaded_files = set()       # Bu artık kullanılmıyor ama istenirse ayar için kalabilir
check_duplicate = False      # Aynı dosya tekrar yüklemeyi engelleme ayarı (default: False)

def tum_verileri_sifirla():
    print("Tüm veriler sıfırlanıyor...")
    if os.path.exists("data"):
        shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)
    print("Data klasörü ve geçmiş temizlendi.")

def excel_yukle(file_path):
    if check_duplicate:
        import hashlib
        with open(file_path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        if file_hash in uploaded_files:
            print("UYARI: Bu dosya daha önce yüklenmiş olabilir.")
        else:
            uploaded_files.add(file_hash)
    print(f"{file_path} başarıyla yüklendi (kontrol yapılmadı veya serbest bırakıldı).")
