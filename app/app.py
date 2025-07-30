
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

# Yüklenen dosyalar listesi
if not os.path.exists(DOSYA_LISTESI):
    pd.DataFrame(columns=["dosya"]).to_csv(DOSYA_LISTESI, index=False)

dosya_listesi = pd.read_csv(DOSYA_LISTESI)
if not dosya_listesi.empty:
    st.subheader("📂 Yüklenen Dosyalar")
    for i, row in dosya_listesi.iterrows():
        col1, col2 = st.columns([4,1])
        col1.write(row["dosya"])
        if col2.button("❌ Sil", key=f"sil_{i}"):
            dosya_listesi = dosya_listesi[dosya_listesi["dosya"] != row["dosya"]]
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
    # Otomatik olarak aynı isimli dosya varsa sil
    if yeni_dosya.name in list(dosya_listesi["dosya"]):
        dosya_listesi = dosya_listesi[dosya_listesi["dosya"] != yeni_dosya.name]
        dosya_listesi.to_csv(DOSYA_LISTESI, index=False)
        if os.path.exists(VERI_DOSYA):
            veri_df = pd.read_csv(VERI_DOSYA)
            veri_df = veri_df[veri_df["kaynak_dosya"] != yeni_dosya.name]
            veri_df.to_csv(VERI_DOSYA, index=False)

    # Yeni dosya kaydı
    dosya_listesi = pd.concat([dosya_listesi, pd.DataFrame([[yeni_dosya.name]], columns=["dosya"])], ignore_index=True)
    dosya_listesi.to_csv(DOSYA_LISTESI, index=False)

    st.success(f"{yeni_dosya.name} başarıyla yüklendi ve eski kayıtlar temizlendi.")
