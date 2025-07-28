import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Firma Bütçe Takip", layout="wide")

st.title("📊 Firma Bütçe Takip Sistemi")

st.sidebar.header("Veri Girişi")

firma = st.sidebar.selectbox("Firma Seçiniz", ["Etki OSGB", "Etki Belgelendirme"])
veri_tipi = st.sidebar.selectbox("Veri Türü", ["Gider", "Gelir"])
veri_ayi = st.sidebar.selectbox("Veri Ayı", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])

uploaded_file = st.file_uploader("Excel Dosyasını Yükleyiniz", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sayfalar = xls.sheet_names
    secilen_sayfa = st.selectbox("Excel Sayfasını Seçiniz", sayfalar)
    df = xls.parse(secilen_sayfa)
    st.success(f"{secilen_sayfa} sayfasından veri okundu.")
    st.dataframe(df)

    if st.button("▶ Aylık Dağılımı Yap ve Uygula"):
        st.info("Dağılım işlemleri daha sonra eklenecek...")
        # Buraya dağılım ve oran hesaplama gelecektir.

st.sidebar.markdown("---")
st.sidebar.button("🔙 Geri Al (Son Yükleme)")