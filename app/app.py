
import streamlit as st
import pandas as pd
import os

ORAN_DOSYA = "data/oranlar.csv"
VERI_DOSYA = "data/yuklenen_veriler.csv"
DOSYA_LISTESI = "data/yuklenen_dosyalar.csv"

st.set_page_config(page_title="Etki OSGB & Belgelendirme", layout="wide")
st.title("📤 Excel'den Gelir/Gider Yükleme")

# Tüm verileri sıfırlama
if st.button("🗑️ Tüm Verileri Sıfırla"):
    if os.path.exists(VERI_DOSYA):
        os.remove(VERI_DOSYA)
    if os.path.exists(DOSYA_LISTESI):
        os.remove(DOSYA_LISTESI)
    st.success("Tüm veriler sıfırlandı.")
    st.rerun()

# Dosya listesi
if not os.path.exists(DOSYA_LISTESI):
    pd.DataFrame(columns=["firma", "ay", "tur", "dosya"]).to_csv(DOSYA_LISTESI, index=False)

dosya_listesi = pd.read_csv(DOSYA_LISTESI)

if not dosya_listesi.empty:
    st.subheader("📂 Yüklenen Dosyalar")
    for i, row in dosya_listesi.iterrows():
        col1, col2 = st.columns([4,1])
        col1.write(f"{row['firma']} | {row['ay']} | {row['tur']} | {row['dosya']}")
        if col2.button("❌ Sil", key=f"sil_{i}"):
            # Eski dosyayı sil
            dosya_listesi = dosya_listesi.drop(i)
            dosya_listesi.to_csv(DOSYA_LISTESI, index=False)

            if os.path.exists(VERI_DOSYA):
                veri_df = pd.read_csv(VERI_DOSYA)
                veri_df = veri_df[veri_df["kaynak_dosya"] != row["dosya"]]
                veri_df.to_csv(VERI_DOSYA, index=False)

            st.rerun()

firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
ay = st.selectbox("Hangi Ay İçin?", ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"])
tur = st.selectbox("Gider mi Gelir mi?", ["Gider", "Gelir"])
yeni_dosya = st.file_uploader("Excel Dosyasını Seçin", type=["xlsx", "xls"])

if yeni_dosya:
    # Eğer aynı firma + ay + tür + dosya adı varsa sil
    mask = (
        (dosya_listesi["firma"] == firma) &
        (dosya_listesi["ay"] == ay) &
        (dosya_listesi["tur"] == tur) &
        (dosya_listesi["dosya"] == yeni_dosya.name)
    )
    if mask.any():
        eski_kayitlar = dosya_listesi[mask]
        dosya_listesi = dosya_listesi[~mask]
        dosya_listesi.to_csv(DOSYA_LISTESI, index=False)

        if os.path.exists(VERI_DOSYA):
            veri_df = pd.read_csv(VERI_DOSYA)
            for _, row in eski_kayitlar.iterrows():
                veri_df = veri_df[veri_df["kaynak_dosya"] != row["dosya"]]
            veri_df.to_csv(VERI_DOSYA, index=False)

    # Yeni kayıt ekle
    yeni_kayit = pd.DataFrame([[firma, ay, tur, yeni_dosya.name]], columns=["firma","ay","tur","dosya"])
    dosya_listesi = pd.concat([dosya_listesi, yeni_kayit], ignore_index=True)
    dosya_listesi.to_csv(DOSYA_LISTESI, index=False)

    st.success(f"✅ {firma} | {ay} | {tur} için {yeni_dosya.name} yüklendi. Eski kayıtlar temizlendi.")
