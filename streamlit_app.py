
import streamlit as st
import pandas as pd
import locale
from datetime import datetime
import calendar

# Locale ayarı: Türkçe ay isimleri
try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
except:
    locale.setlocale(locale.LC_TIME, "Turkish_Turkey")

st.title("Firma Bütçe Takip ve Aylık Dağılım")

firma = st.selectbox("Firma Seçin", ["Etki Akademi", "Etki Osgb"])
veri_tipi = st.selectbox("Veri Tipi", ["Gider", "Gelir"])
secili_ay = st.selectbox("Hangi Ayın Verisi", list(calendar.month_name)[1:])

yuklenen_dosya = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx"])
if yuklenen_dosya:
    df = pd.read_excel(yuklenen_dosya)

    if not all(k in df.columns for k in ["TARİH", "HESAP İSMİ", "ANA DÖVİZ BORÇ", "Gider Başlangıç", "Gider Bitiş Tarihi"]):
        st.error("Excel dosyasında gerekli sütunlar bulunmuyor.")
    else:
        def aylara_dagit(row):
            baslangic = str(row["Gider Başlangıç"])
            bitis = str(row["Gider Bitiş Tarihi"])
            try:
                start = pd.to_datetime("01 " + baslangic, dayfirst=True)
                end = pd.to_datetime("01 " + bitis, dayfirst=True)
                months = pd.date_range(start, end, freq="MS")
                tutar = row["ANA DÖVİZ BORÇ"] / len(months)
                data = {
                    "HESAP İSMİ": row["HESAP İSMİ"],
                    "FİRMA": firma,
                    "VERİ TİPİ": veri_tipi,
                }
                for m in months:
                    ay_ad = m.strftime("%B")
                    data[ay_ad] = round(tutar, 2)
                return pd.DataFrame([data])
            except:
                return pd.DataFrame()

        dagilim_df = pd.concat([aylara_dagit(row) for _, row in df.iterrows()], ignore_index=True)

        if not dagilim_df.empty:
            st.success("Aylık dağılım başarıyla oluşturuldu.")
            st.dataframe(dagilim_df)

            toplamlar = dagilim_df.drop(columns=["HESAP İSMİ", "FİRMA", "VERİ TİPİ"]).sum()
            st.bar_chart(toplamlar)
        else:
            st.warning("Dağılım oluşturulamadı. Tarihler kontrol edilmeli.")
