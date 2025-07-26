
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Firma Bütçe Takip ve Aylık Dağıtım Uygulaması")

# Türkçe ay haritası
ay_harita = {
    "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan",
    "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos",
    "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
}

def aylara_dagit(df, veri_giris_ayi):
    dagilimlar = []
    for _, row in df.iterrows():
        try:
            baslangic = pd.to_datetime(row["Gider Başlangıç"], dayfirst=True)
            bitis = pd.to_datetime(row["Gider Bitiş Tarihi"], dayfirst=True)
        except:
            continue

        if pd.isna(baslangic) or pd.isna(bitis):
            continue

        ay_sayisi = (bitis.year - baslangic.year) * 12 + (bitis.month - baslangic.month) + 1
        if ay_sayisi <= 0:
            continue

        tutar = row["ANA DÖVİZ BORÇ"] / ay_sayisi

        for i in range(ay_sayisi):
            ay = baslangic + pd.DateOffset(months=i)
            ay_adi = ay_harita[ay.strftime("%B")] + f" {ay.year}"
            dagilimlar.append({
                "Hesap": row["HESAP İSMİ"],
                "Firma": row["Firma"],
                "Tür": row["Tür"],
                "Ay": ay_adi,
                "Tutar": round(tutar, 2),
                "Veri Giriş Ayı": veri_giris_ayi
            })

    return pd.DataFrame(dagilimlar)

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx"])
firma = st.selectbox("Firma Seçin", ["Etki Akademi", "Etki Osgb"])
veri_tipi = st.selectbox("Veri Tipi", ["Gider", "Gelir"])
veri_ay = st.selectbox("Bu veriler hangi aya ait?", [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
])
veri_giris_ayi = f"{veri_ay} {datetime.now().year}"

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Firma"] = firma
    df["Tür"] = veri_tipi

    if "Gider Başlangıç" in df.columns and "Gider Bitiş Tarihi" in df.columns and "ANA DÖVİZ BORÇ" in df.columns:
        dagilim_df = aylara_dagit(df, veri_giris_ayi)
        st.success("Aylık dağılım oluşturuldu")
        st.dataframe(dagilim_df)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            dagilim_df.to_excel(writer, index=False, sheet_name="Aylık Dağılım")
        st.download_button(label="Aylık Dağılım Excel İndir", data=buffer.getvalue(),
                           file_name="aylik_dagilim.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.error("Excel dosyasında gerekli sütunlar bulunamadı.")
