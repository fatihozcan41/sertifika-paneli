import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Etki Gelir Gider Takibi", layout="wide")
st.title("💼 Etki OSGB / Etki Belgelendirme Gelir Gider Takibi")

VERI_DOSYA = "data/veriler.csv"
ORAN_DOSYA = "data/oranlar.csv"

# Giriş Paneli
st.header("📥 Veri Girişi")
with st.form("veri_form"):
    firma = st.selectbox("Firma Seçiniz", ["Etki OSGB", "Etki Belgelendirme"])
    tur = st.radio("İşlem Türü", ["Gelir", "Gider"])
    ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
    tarih = st.date_input("Tarih", value=date.today())
    hesap_ismi = st.text_input("Hesap İsmi")
    tutar = st.number_input("Tutar", min_value=0.0, format="%.2f")
    sorumluluk = st.text_input("Sorumluluk Merkezi")
    gonder = st.form_submit_button("Veriyi Kaydet")

    if gonder:
        if not hesap_ismi:
            st.warning("Hesap ismi girilmelidir.")
        else:
            yeni = pd.DataFrame([{
                "firma": firma,
                "tur": tur,
                "ay": ay,
                "tarih": tarih,
                "hesap_ismi": hesap_ismi,
                "tutar": tutar,
                "sorumluluk": sorumluluk
            }])
            if os.path.exists(VERI_DOSYA):
                mevcut = pd.read_csv(VERI_DOSYA)
                df = pd.concat([mevcut, yeni], ignore_index=True)
            else:
                df = yeni
            df.to_csv(VERI_DOSYA, index=False)
            st.success("✅ Veri kaydedildi.")
