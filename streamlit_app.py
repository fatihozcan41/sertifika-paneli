
import streamlit as st
import pandas as pd
import datetime
import locale

# Türkçe ay isimleri için locale ayarla
try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
except:
    locale.setlocale(locale.LC_TIME, "turkish")

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

def aylara_dagit(row):
    try:
        baslangic = pd.to_datetime(row["Gider Başlangıç"], errors="coerce")
        bitis = pd.to_datetime(row["Gider Bitiş Tarihi"], errors="coerce")
        if pd.isna(baslangic) or pd.isna(bitis):
            return pd.DataFrame()
        aylar_arasi = pd.date_range(start=baslangic, end=bitis, freq='MS')
        if len(aylar_arasi) == 0:
            return pd.DataFrame()
        tutar = row["ANA DÖVİZ BORÇ"] / len(aylar_arasi)
        return pd.DataFrame({
            "Firma": [firma] * len(aylar_arasi),
            "Veri Tipi": [veri_tipi] * len(aylar_arasi),
            "HESAP İSMİ": [row["HESAP İSMİ"]] * len(aylar_arasi),
            "Yıl": [d.year for d in aylar_arasi],
            "Ay": [d.strftime("%B") for d in aylar_arasi],
            "Tutar": [round(tutar, 2)] * len(aylar_arasi)
        })
    except:
        return pd.DataFrame()

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        st.success(f"{firma} - {veri_tipi} verisi başarıyla yüklendi ({secili_ay} {yil})")
        st.subheader("Yüklenen Veri")
        st.dataframe(df)

        dagilim_df = pd.concat([aylara_dagit(row) for _, row in df.iterrows()], ignore_index=True)

        if not dagilim_df.empty:
            st.subheader("📅 Aylık Dağılım Tablosu")
            dagilim_df["Ay"] = pd.to_datetime(dagilim_df["Ay"], format="%B").dt.strftime("%B")  # Türkçe görünüm
            dagilim_df["Ay"] = dagilim_df["Ay"].apply(lambda x: x.capitalize())  # Ay adlarını büyük harfle başlat
            st.dataframe(dagilim_df)

            st.subheader("📈 Gider Türlerine Göre Dağılım")
            toplamlar = dagilim_df.groupby("HESAP İSMİ")["Tutar"].sum().reset_index()
            st.dataframe(toplamlar)

            st.bar_chart(dagilim_df.groupby(["Yıl", "Ay"])["Tutar"].sum())

        else:
            st.warning("Dağılım yapılacak geçerli veri bulunamadı.")

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
