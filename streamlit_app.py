
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Firma Bütçe Takip", layout="wide")

st.title("Firma Bütçe Takip Sistemi")

firma_adi = st.selectbox("Firma Seçiniz", ["Etki Akademi", "Etki Osgb"])
veri_tipi = st.selectbox("Veri Türü", ["Gider", "Gelir"])
secili_ay = st.selectbox("Ay Seçiniz", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                                        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
uploaded_file = st.file_uploader("Excel dosyasını yükleyiniz", type=["xlsx"])

ay_adlari = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

def aylara_dagit(df):
    sonuc = []
    for _, row in df.iterrows():
        baslangic = pd.to_datetime(row["Gider Başlangıç"])
        bitis = pd.to_datetime(row["Gider Bitiş Tarihi"])
        if pd.isnull(baslangic) or pd.isnull(bitis):
            continue
        ay_sayisi = (bitis.year - baslangic.year) * 12 + (bitis.month - baslangic.month + 1)
        if ay_sayisi <= 0:
            continue
        tutar = row["ANA DÖVİZ BORÇ"]
        if pd.isnull(tutar) or tutar == 0:
            continue
        aylik_tutar = tutar / ay_sayisi
        for i in range(ay_sayisi):
            ay = (baslangic.month + i - 1) % 12 + 1
            yil = baslangic.year + (baslangic.month + i - 1) // 12
            ay_adi = ay_adlari[ay]
            sonuc.append({
                "Firma": firma_adi,
                "Yıl": yil,
                "Ay": ay_adi,
                "Hesap": row["HESAP İSMİ"],
                "Tutar": round(aylik_tutar, 2)
            })
    return pd.DataFrame(sonuc)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if "Gider Başlangıç" in df.columns and "Gider Bitiş Tarihi" in df.columns:
        dagilim_df = aylara_dagit(df)
        st.success("Dağılım başarıyla yapıldı.")
        st.dataframe(dagilim_df)
        csv = dagilim_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Dağılımı İndir (CSV)", data=csv, file_name="dagilim.csv", mime="text/csv")
    else:
        st.error("Excel dosyasında 'Gider Başlangıç' ve 'Gider Bitiş Tarihi' sütunları olmalı.")
