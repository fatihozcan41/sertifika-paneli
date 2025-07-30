
import pandas as pd
import streamlit as st

st.title("Etki Budget App - Temel Versiyon (v52)")

# Örnek veri
data = [
    {"HESAP İSMİ": "Elektrik", "Başlangıç": "Oca.25", "Bitiş": "Mar.25", "Tutar": 3000},
    {"HESAP İSMİ": "Su", "Başlangıç": "Oca.25", "Bitiş": "Şub.25", "Tutar": 2000}
]

df = pd.DataFrame(data)

sonuc = []
for _, row in df.iterrows():
    try:
        bas_tarih = pd.to_datetime(row["Başlangıç"], format="%b.%y")
    except ValueError:
        bas_tarih = pd.to_datetime(row["Başlangıç"], dayfirst=True, errors="coerce")
    try:
        bit_tarih = pd.to_datetime(row["Bitiş"], format="%b.%y")
    except ValueError:
        bit_tarih = pd.to_datetime(row["Bitiş"], dayfirst=True, errors="coerce")
    if pd.isna(bas_tarih) or pd.isna(bit_tarih):
        st.warning(f"⚠️ {row['HESAP İSMİ']} için Başlangıç veya Bitiş tarihi hatalı. Tutar tek seferde listelendi.")
        ay_listesi = []
    else:
        ay_listesi = pd.date_range(bas_tarih, bit_tarih, freq="MS")
    toplam_tutar = row["Tutar"]

    # Güvenli tutar_aylik hesaplaması
    if ay_listesi is not None and len(ay_listesi) > 0:
        tutar_aylik = toplam_tutar / len(ay_listesi)
    else:
        st.warning("⚠️ Başlangıç ve Bitiş aralığında ay bulunamadı. Tutar tek seferde listelendi.")
        tutar_aylik = toplam_tutar
        ay_listesi = [bas_tarih]

    if not ay_listesi:
        sonuc.append({
            "HESAP İSMİ": row["HESAP İSMİ"],
            "Ay": "Tek Sefer",
            "Tutar (Aylık)": round(toplam_tutar, 2)
        })
    else:
        for ay in ay_listesi:
            if pd.isna(ay):
                sonuc.append({
                    "HESAP İSMİ": row["HESAP İSMİ"],
                    "Ay": "Tek Sefer",
                    "Tutar (Aylık)": round(toplam_tutar, 2)
                })
            else:
                sonuc.append({
                    "HESAP İSMİ": row["HESAP İSMİ"],
                    "Ay": ay.strftime("%Y-%m"),
                    "Tutar (Aylık)": round(tutar_aylik, 2)
                })

# Sonuç DataFrame
sonuc_df = pd.DataFrame(sonuc)
st.subheader("Ay Bazlı Dağılım")
st.dataframe(sonuc_df)
