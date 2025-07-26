
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="Bütçe Yönetimi", layout="wide")
st.title("📊 Firma Bazlı Bütçe Dağılım Sistemi")

uploaded_file = st.file_uploader("Excel gider dosyasını yükle (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Dosya yüklendi ve analiz ediliyor...")

    df["Gider Başlangıç"] = pd.to_datetime(df["Gider Başlangıç"])
    df["Gider Bitiş Tarihi"] = pd.to_datetime(df["Gider Bitiş Tarihi"])
    df["TARİH"] = pd.to_datetime(df["TARİH"])
    df = df[df["Gider Başlangıç"].astype(str).str.lower() != "ciroya dahil etme"]

    def aylara_dagit(row):
        tarih_araligi = pd.date_range(start=row["Gider Başlangıç"], end=row["Gider Bitiş Tarihi"], freq="MS")
        tutar = row["ANA DÖVİZ BORÇ"]
        esik = round(tutar / len(tarih_araligi), 2)
        return pd.DataFrame({
            "FİRMA": row["FİRMA"],
            "HESAP İSMİ": row["HESAP İSMİ"],
            "YIL": tarih_araligi.year,
            "AY": tarih_araligi.month,
            "TUTAR": esik
        })

    dagilim_df = pd.concat([aylara_dagit(row) for _, row in df.iterrows()], ignore_index=True)

    firma_sec = st.selectbox("Firma Seçin", sorted(dagilim_df["FİRMA"].unique()))
    yil_sec = st.selectbox("Yıl Seçin", sorted(dagilim_df["YIL"].unique()))

    filtre = dagilim_df[(dagilim_df["FİRMA"] == firma_sec) & (dagilim_df["YIL"] == yil_sec)]
    pivot = filtre.pivot_table(index="AY", values="TUTAR", aggfunc="sum").reindex(range(1,13), fill_value=0)

    st.subheader("🧾 Aylık Toplam Giderler")
    st.bar_chart(pivot)

    st.subheader("📂 Gider Türü Dağılımı (Yıllık)")
    gider_pasta = filtre.groupby("HESAP İSMİ")["TUTAR"].sum().reset_index()
    fig = px.pie(gider_pasta, names="HESAP İSMİ", values="TUTAR", title="Gider Türü Dağılımı")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 Dağıtılmış Tablonun Detayı"):
        st.dataframe(filtre)

    st.success("Veriler başarıyla işlendi ve görselleştirildi.")
else:
    st.info("Lütfen bir Excel dosyası yükleyin.")
