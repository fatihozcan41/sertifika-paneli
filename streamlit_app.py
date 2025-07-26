
import streamlit as st
import pandas as pd
from pathlib import Path
import shutil

st.set_page_config(layout="wide")
st.title("📂 Yüklenen Tüm Dosyalar")

arsiv_klasoru = Path("veri_arsivi")
arsiv_klasoru.mkdir(exist_ok=True)

dosya_listesi = list(arsiv_klasoru.glob("*.csv"))

if not dosya_listesi:
    st.warning("Henüz arşivlenmiş dosya bulunmamaktadır.")
else:
    for dosya in dosya_listesi:
        with open(dosya, "rb") as f:
            st.download_button(label=f"{dosya.name} indir", data=f, file_name=dosya.name)
