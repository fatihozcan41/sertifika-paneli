
# v46 main uygulama dosyası
# 'Bu dosya zaten yüklenmiş' uyarısı ve tüm kontrol mekanizmaları tamamen kaldırıldı.

import os
import shutil

def tum_verileri_sifirla():
    print("Tüm veriler ve session state temizleniyor...")
    # Data klasörünü temizle
    if os.path.exists("data"):
        shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)

    # Streamlit state temizliği (varsa)
    try:
        import streamlit as st
        st.session_state.clear()
        print("Streamlit session_state temizlendi.")
    except:
        print("Streamlit modülü yok veya session_state kullanılmıyor.")

def excel_yukle(file_path):
    # Artık hiçbir kontrol yapılmıyor, her dosya yüklenebilir
    print(f"{file_path} başarıyla yüklendi. (Kontrol yapılmadı)")
