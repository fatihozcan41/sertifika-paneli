
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Bütçe Takip Sistemi", layout="wide")
st.title("📊 Firma Bütçe Takip Sistemi")

# Firma seçimi
firma = st.selectbox("Firma Seçin", ["Etki Akademi", "Etki Osgb"])

# Veri tipi seçimi
veri_tipi = st.selectbox("Veri Tipi", ["Gider", "Gelir"])

# Ay seçimi
bugun = datetime.date.today()
yil = bugun.year
aylar = [datetime.date(yil, m, 1).strftime("%B") for m in range(1, 13)]
secili_ay = st.selectbox("Hangi ayın verisi giriliyor?", aylar, index=bugun.month - 1)

# Excel yükleme
uploaded_file = st.file_uploader("Excel dosyasını yükleyin (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df["Firma"] = firma
        df["Veri Tipi"] = veri_tipi
        df["Yıl"] = yil
        df["Ay"] = secili_ay

        st.success(f"{firma} - {veri_tipi} verisi başarıyla yüklendi ({secili_ay} {yil})")
        st.dataframe(df)

        # İsteğe bağlı grafik
        if "ANA DÖVİZ BORÇ" in df.columns:
            st.subheader("Toplam Tutar (Ana Döviz Borç)")
            toplam = df["ANA DÖVİZ BORÇ"].sum()
            st.metric("Toplam Tutar", f"{toplam:,.2f} TL")

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
