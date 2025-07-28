
import streamlit as st
import pandas as pd
import os
import datetime
from io import BytesIO
from utils.oran_paneli import oran_giris_paneli
from utils.grafikler import grafik_goster
from utils.pivot_olustur import pivotlari_goster
from utils.dosya_islemleri import yuklenen_dosyalari_getir, geri_al, veri_kaydet, dagit_ve_kaydet

st.set_page_config(layout="wide")
st.title("Firma Bütçe Takip Sistemi")

# 1. Firma seçimi
firma_adi = st.selectbox("Firma Seçin", ["Etki OSGB", "Etki Belgelendirme"])

# 2. Veri tipi seçimi
veri_tipi = st.selectbox("Veri Tipi", ["Gider", "Gelir"])

# 3. Ay seçimi
ay_isimleri = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
               "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
veri_ayi = st.selectbox("Veri Ayı", ay_isimleri)

# 4. Dosya yükleme
yuklenen_dosya = st.file_uploader("Excel Dosyasını Yükleyin", type=["xlsx"])
if yuklenen_dosya:
    sayfalar = pd.ExcelFile(yuklenen_dosya).sheet_names
    secilen_sayfa = st.selectbox("Sayfa Seçin", sayfalar)

    if st.button("Veriyi Yükle ve Dağıt"):
        df = pd.read_excel(yuklenen_dosya, sheet_name=secilen_sayfa)
        oran_df = oran_giris_paneli(df, firma_adi)
        dagit_ve_kaydet(df, firma_adi, veri_tipi, veri_ayi, oran_df)
        st.success("Veriler başarıyla işlendi ve dağıtıldı.")

# 5. Oran Giriş Paneli (dosya yüklendikten sonra yukarıda entegre edildi)

# 6. Geri alma butonu
if st.button("Son Yüklemeyi Geri Al"):
    mesaj = geri_al(firma_adi, veri_tipi, veri_ayi)
    st.warning(mesaj)

# 7. Pivot Görünüm ve 8. Grafikler
st.subheader("Pivot Tablolar ve Grafikler")
pivotlari_goster(firma_adi)
grafik_goster(firma_adi)

# 9. Yüklenen tüm dosyalar
st.sidebar.title("Yüklenen Dosyalar")
st.sidebar.write(yuklenen_dosyalari_getir())
