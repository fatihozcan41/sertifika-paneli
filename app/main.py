
# v47 main uygulama dosyası
# Frontend ve backend entegre: uploader resetleniyor, 'zaten yüklenmiş' uyarısı kaldırıldı.

import os
import shutil
import streamlit as st

# Reset için session key
if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0

def tum_verileri_sifirla():
    # Backend temizliği
    if os.path.exists("data"):
        shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)
    # Frontend reset
    st.session_state.reset_key += 1
    st.session_state.clear()
    st.success("Tüm veriler ve yükleme listesi sıfırlandı.")

def excel_yukle():
    uploaded_file = st.file_uploader(
        "Excel Dosyasını Seçin", 
        type=["xls", "xlsx"], 
        key=st.session_state.reset_key
    )
    if uploaded_file is not None:
        st.success(f"{uploaded_file.name} başarıyla yüklendi.")
        # Burada dosya işleme logic'i
        return uploaded_file

# UI
st.title("Yüklenen Dosyalar")
if st.button("Tüm Verileri Sıfırla"):
    tum_verileri_sifirla()

file = excel_yukle()
if file:
    st.write("Dosya işleniyor...")
