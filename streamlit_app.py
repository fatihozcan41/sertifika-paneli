
import streamlit as st
import pandas as pd
import datetime

st.title("Aylık Gider Dağılım Uygulaması")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin (.xlsx)", type="xlsx")

def aylara_dagit(row):
    try:
        baslangic = pd.to_datetime(row["Gider Başlangıç"])
        bitis = pd.to_datetime(row["Gider Bitiş Tarihi"])
    except:
        return pd.DataFrame()

    if isinstance(row["Gider Başlangıç"], str) and "ciroya dahil etme" in row["Gider Başlangıç"].lower():
        return pd.DataFrame()  # Ciroya dahil olmayanları atla

    aylar = pd.date_range(baslangic, bitis, freq='MS')  # Her ayın başı
    tutar = row["ANA DÖVİZ BORÇ"] / len(aylar) if len(aylar) > 0 else 0

    return pd.DataFrame({
        "HESAP İSMİ": [row["HESAP İSMİ"]] * len(aylar),
        "YIL": [d.year for d in aylar],
        "AY": [d.strftime("%B") for d in aylar],
        "TUTAR": [tutar] * len(aylar)
    })

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()  # Başlıklardaki boşlukları temizle

    try:
        dagilim_df = pd.concat([aylara_dagit(row) for _, row in df.iterrows()], ignore_index=True)

        st.subheader("Aylık Dağılım Tablosu")
        st.dataframe(dagilim_df)

        st.subheader("Toplam Gider Grafiği")
        grafik_df = dagilim_df.groupby(["YIL", "AY"]).sum(numeric_only=True).reset_index()
        st.bar_chart(grafik_df.pivot(index="AY", columns="YIL", values="TUTAR"))

        st.subheader("Gider Türlerine Göre Dağılım")
        gider_turleri = dagilim_df.groupby("HESAP İSMİ")["TUTAR"].sum().reset_index()
        st.dataframe(gider_turleri)
        st.plotly_chart(
            {
                "data": [{"labels": gider_turleri["HESAP İSMİ"], "values": gider_turleri["TUTAR"], "type": "pie"}],
                "layout": {"title": "Gider Türlerine Göre Dağılım"}
            }
        )
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
