
# v49 app.py - Tüm girintileme (indentation) hataları giderildi, PEP8 formatında

import os
import shutil
import pandas as pd
import streamlit as st


def tum_verileri_sifirla():
    """Tüm verileri, session ve uploader'ı sıfırlar"""
    if os.path.exists("data"):
        shutil.rmtree("data")
        os.makedirs("data", exist_ok=True)

    if "reset_key" not in st.session_state:
        st.session_state.reset_key = 0

    st.session_state.reset_key += 1
    st.session_state.clear()
    st.success("Tüm veriler ve yükleme listesi sıfırlandı.")


def excel_yukle():
    """Excel dosyasını yükler ve okur"""
    uploaded_file = st.file_uploader(
        "Excel Dosyasını Seçin",
        type=["xls", "xlsx"],
        key=st.session_state.get("reset_key", 0)
    )

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        for index, row in df.iterrows():
            bas = pd.to_datetime(row["bas"]) if pd.notna(row.get("bas")) else None
            bitis = pd.to_datetime(row["bitis"]) if pd.notna(row.get("bitis")) else None
            # Burada diğer işleme adımları yapılabilir

        st.success(f"{uploaded_file.name} başarıyla yüklendi.")
        return df

    return None


# Uygulama arayüzü
st.title("Yüklenen Dosyalar")

if st.button("Tüm Verileri Sıfırla"):
    tum_verileri_sifirla()

data = excel_yukle()

if data is not None:
    st.write("Yüklenen veri örneği:", data.head())
