
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import os

st.set_page_config(layout="wide")
st.title("Firma Bütçe Takip ve Aylık Dağıtım Uygulaması")

# Türkçe ay haritası
ay_harita = {
    "January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan",
    "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos",
    "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"
}
aylar_sirali = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]
veri_cache_path = "veri_cache.csv"
arsiv_klasoru = "arsiv"

os.makedirs(arsiv_klasoru, exist_ok=True)

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
veri_ay = st.selectbox("Bu veriler hangi aya ait?", aylar_sirali)
veri_giris_ayi = f"{veri_ay} {datetime.now().year}"

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df["Firma"] = firma
    df["Tür"] = veri_tipi

    if "Gider Başlangıç" in df.columns and "Gider Bitiş Tarihi" in df.columns and "ANA DÖVİZ BORÇ" in df.columns:
        yeni_df = aylara_dagit(df, veri_giris_ayi)

        # Mevcut veri varsa oku
        if os.path.exists(veri_cache_path):
            eski_df = pd.read_csv(veri_cache_path)
            # Aynı Hesap+Firma+Veri Giriş Ayı olanları sil
            filtre = ~((eski_df["Firma"] == firma) & 
                       (eski_df["Tür"] == veri_tipi) &
                       (eski_df["Veri Giriş Ayı"] == veri_giris_ayi) &
                       (eski_df["Hesap"].isin(yeni_df["Hesap"].unique())))
            eski_df = eski_df[filtre]
            birlesik_df = pd.concat([eski_df, yeni_df], ignore_index=True)
        else:
            birlesik_df = yeni_df

        # Cache ve arşivle
        birlesik_df.to_csv(veri_cache_path, index=False)
        now_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        arsiv_yolu = os.path.join(arsiv_klasoru, f"{firma}_{veri_giris_ayi}_{now_str}.csv")
        df.to_csv(arsiv_yolu, index=False)

        st.success("Veri eklendi. Önceki aynı hesaplar güncellendi. Arşivlendi.")
        st.dataframe(birlesik_df)

        # Pivot tablo
        aylar_yil = [f"{ay} {datetime.now().year}" for ay in aylar_sirali]
        pivot_df = birlesik_df.pivot_table(index="Hesap", columns="Ay", values="Tutar", aggfunc="sum").fillna(0)
        pivot_df = pivot_df.reindex(columns=aylar_yil, fill_value=0).reset_index()
        st.subheader("Pivot Formatında Görünüm")
        st.dataframe(pivot_df)

        # Excel çıktısı
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            birlesik_df.to_excel(writer, index=False, sheet_name="Tüm Dağılım")
            pivot_df.to_excel(writer, index=False, sheet_name="Pivot Dağılım")
        st.download_button(label="Excel İndir (Tüm + Pivot)", data=buffer.getvalue(),
                           file_name="tum_aylik_dagilim_pivot.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.error("Excel dosyasında gerekli sütunlar bulunamadı.")
