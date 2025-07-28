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

st.header("⚙️ Oran Tanımlama Paneli")

oranlar_df = pd.read_csv(ORAN_DOSYA) if os.path.exists(ORAN_DOSYA) else pd.DataFrame(
    columns=["hesap_ismi", "osgb", "belge", "egitim", "ilkyardim", "kalite", "uzmanlik"]
)

with st.form("oran_form"):
    st.markdown("Ortak gider içeren bir *HESAP İSMİ* için oranları tanımlayın.")
    hesap_ismi_input = st.text_input("Hesap İsmi (BELGE ORTAK GİDER ya da OSGB + BELGE ORTAK GİDER altında geçen)")
    osgb_oran = st.slider("Etki OSGB Oranı (%)", 0, 100, 50)
    belge_oran = 100 - osgb_oran

    st.markdown(f"Etki Belgelendirme oranı: **{belge_oran}%** → alt kırılım:")
    egitim = st.slider("EĞİTİM (%)", 0, belge_oran, 25)
    ilkyardim = st.slider("İLKYARDIM (%)", 0, belge_oran - egitim, 25)
    kalite = st.slider("KALİTE (%)", 0, belge_oran - egitim - ilkyardim, 25)
    uzmanlik = belge_oran - egitim - ilkyardim - kalite
    st.markdown(f"UZMANLIK: **{uzmanlik}%** (Otomatik hesaplandı)")

    oran_gonder = st.form_submit_button("Oranı Kaydet")

    if oran_gonder:
        if not hesap_ismi_input:
            st.warning("Hesap ismi girmelisiniz.")
        else:
            yeni_kayit = pd.DataFrame([{
                "hesap_ismi": hesap_ismi_input,
                "osgb": osgb_oran,
                "belge": belge_oran,
                "egitim": egitim,
                "ilkyardim": ilkyardim,
                "kalite": kalite,
                "uzmanlik": uzmanlik
            }])
            # varsa eskiyi silip yeni kaydı ekle
            oranlar_df = oranlar_df[oranlar_df["hesap_ismi"] != hesap_ismi_input]
            oranlar_df = pd.concat([oranlar_df, yeni_kayit], ignore_index=True)
            oranlar_df.to_csv(ORAN_DOSYA, index=False)
            st.success("✅ Oran tanımı kaydedildi.")

st.header("📊 Raporlama Paneli")

if os.path.exists(VERI_DOSYA):
    df = pd.read_csv(VERI_DOSYA)

    with st.expander("🔍 Filtreleme Seçenekleri", expanded=True):
        firma_filtresi = st.multiselect("Firma", df["firma"].unique(), default=df["firma"].unique())
        ay_filtresi = st.multiselect("Ay", df["ay"].unique(), default=df["ay"].unique())
        tur_filtresi = st.multiselect("Tür", df["tur"].unique(), default=df["tur"].unique())

    filtreli = df[
        (df["firma"].isin(firma_filtresi)) &
        (df["ay"].isin(ay_filtresi)) &
        (df["tur"].isin(tur_filtresi))
    ]

    toplamlar = filtreli.groupby(["firma", "tur", "ay"])["tutar"].sum().reset_index()
    st.dataframe(toplamlar, use_container_width=True)

    import plotly.express as px
    grafik = px.bar(
        toplamlar,
        x="ay", y="tutar", color="tur",
        barmode="group", facet_col="firma",
        title="Gelir/Gider Karşılaştırması"
    )
    st.plotly_chart(grafik, use_container_width=True)
else:
    st.info("Henüz veri girişi yapılmamış.")
