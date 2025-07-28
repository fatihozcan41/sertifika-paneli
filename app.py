import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px
from io import BytesIO

# CSV dosya yolları
VERI_DOSYA = "veriler.csv"
ORAN_DOSYA = "oranlar.csv"

st.set_page_config(page_title="Etki Bütçe Takip Sistemi", layout="wide")
st.title("📊 Etki OSGB & Belgelendirme Bütçe Takip Sistemi")

# CSV dosyaları yoksa oluştur
if not os.path.exists(VERI_DOSYA):
    pd.DataFrame(columns=["firma", "tur", "ay", "tarih", "hesap_ismi", "tutar", "sorumluluk"]).to_csv(VERI_DOSYA, index=False)
if not os.path.exists(ORAN_DOSYA):
    pd.DataFrame(columns=["hesap_ismi", "osgb", "belge", "egitim", "ilkyardim", "kalite", "uzmanlik"]).to_csv(ORAN_DOSYA, index=False)

menu = st.sidebar.radio("Menü Seçimi", ["📥 Veri Girişi", "⚖️ Oran Tanımı", "📈 Raporlama", "📤 Excel Dışa Aktar"])

if menu == "📥 Veri Girişi":
    st.subheader("➕ Veri Girişi")
    with st.form("veri_formu"):
        firma = st.selectbox("Firma Seçiniz", ["Etki OSGB", "Etki Belgelendirme"])
        tur = st.radio("İşlem Türü", ["Gelir", "Gider"], horizontal=True)
        ay = st.selectbox("Ay", list(pd.date_range('2024-01-01', '2024-12-01', freq='MS').strftime('%B')))
        tarih = st.date_input("Tarih", value=date.today())
        hesap_ismi = st.text_input("Hesap İsmi")
        tutar = st.number_input("Tutar (₺)", min_value=0.0, format="%.2f")
        sorumluluk = st.text_input("Sorumluluk Merkezi")

        submitted = st.form_submit_button("Veriyi Kaydet")
        if submitted:
            if not hesap_ismi:
                st.warning("Hesap ismi giriniz.")
            else:
                yeni_veri = pd.DataFrame([{
                    "firma": firma,
                    "tur": tur,
                    "ay": ay,
                    "tarih": tarih,
                    "hesap_ismi": hesap_ismi,
                    "tutar": tutar,
                    "sorumluluk": sorumluluk
                }])
                yeni_veri.to_csv(VERI_DOSYA, mode="a", header=False, index=False)
                st.success("Veri başarıyla kaydedildi!")

elif menu == "⚖️ Oran Tanımı":
    st.subheader("🧮 Oran Tanımlama")
    with st.form("oran_formu"):
        hesap_oran_ismi = st.text_input("Oran için HESAP İSMİ", key="oranhesap")
        col1, col2 = st.columns(2)
        with col1:
            osgb_oran = st.number_input("Etki OSGB (%)", min_value=0, max_value=100, value=40)
        with col2:
            belge_oran = st.number_input("Etki Belgelendirme (%)", min_value=0, max_value=100, value=60)

        st.caption("Aşağıdaki oranlar yalnızca Etki Belgelendirme oranı içindir:")
        col3, col4 = st.columns(2)
        with col3:
            egitim = st.number_input("EĞİTİM (%)", min_value=0, max_value=100, value=25)
            kalite = st.number_input("KALİTE DANIŞMANLIK (%)", min_value=0, max_value=100, value=30)
        with col4:
            ilkyardim = st.number_input("İLKYARDIM (%)", min_value=0, max_value=100, value=25)
            uzmanlik = st.number_input("UZMANLIK (%)", min_value=0, max_value=100, value=20)

        oran_gonder = st.form_submit_button("Oranları Kaydet")
        if oran_gonder:
            if not hesap_oran_ismi:
                st.error("Hesap ismi giriniz.")
            elif osgb_oran + belge_oran != 100:
                st.error("OSGB ve Belgelendirme toplamı %100 olmalı!")
            elif egitim + ilkyardim + kalite + uzmanlik != 100:
                st.error("Alt dağılım oranları %100 olmalı!")
            else:
                oranlar = pd.read_csv(ORAN_DOSYA)
                oranlar = oranlar[oranlar["hesap_ismi"] != hesap_oran_ismi]
                yeni_oran = pd.DataFrame([{
                    "hesap_ismi": hesap_oran_ismi,
                    "osgb": osgb_oran,
                    "belge": belge_oran,
                    "egitim": egitim,
                    "ilkyardim": ilkyardim,
                    "kalite": kalite,
                    "uzmanlik": uzmanlik
                }])
                oranlar = pd.concat([oranlar, yeni_oran])
                oranlar.to_csv(ORAN_DOSYA, index=False)
                st.success("Oran başarıyla kaydedildi!")

elif menu == "📈 Raporlama":
    st.subheader("📊 Aylık & Firma Bazlı Raporlama")
    df = pd.read_csv(VERI_DOSYA)
    if df.empty:
        st.info("Henüz veri girişi yapılmamış.")
    else:
        filtre_ay = st.selectbox("Ay Filtresi", sorted(df["ay"].unique()))
        filtre_firma = st.multiselect("Firma Filtresi", df["firma"].unique(), default=list(df["firma"].unique()))
        df_filt = df[(df["ay"] == filtre_ay) & (df["firma"].isin(filtre_firma))]

        st.dataframe(df_filt.style.format({"tutar": "₺{:.2f}"}), use_container_width=True)

        gruplu = df_filt.groupby(["firma", "tur"])["tutar"].sum().reset_index()
        fig = px.bar(gruplu, x="firma", y="tutar", color="tur", barmode="group", title="Firma Bazlı Gelir/Gider Dağılımı")
        st.plotly_chart(fig, use_container_width=True)

elif menu == "📤 Excel Dışa Aktar":
    st.subheader("📤 Excel İndir")
    df = pd.read_csv(VERI_DOSYA)
    oran_df = pd.read_csv(ORAN_DOSYA)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Veriler')
        oran_df.to_excel(writer, index=False, sheet_name='Oranlar')

    st.download_button("📥 Excel İndir", data=buffer.getvalue(), file_name="etki-butce-veriler.xlsx")
