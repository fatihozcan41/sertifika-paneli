import pandas as pd
import streamlit as st

st.title("Dağıtım ve Oranlama Uygulaması - v33")

# Excel yükleme
uploaded_file = st.file_uploader("Girdi tablosunu yükleyin (Excel)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("Girdi Tablosu")
    st.dataframe(df)

    # oranlar.csv yükleme
    oranlar_file = st.file_uploader("oranlar.csv yükleyin", type=["csv"])

    if oranlar_file:
        oranlar_df = pd.read_csv(oranlar_file)
        st.subheader("Oranlar Tablosu")
        st.dataframe(oranlar_df)

        # oranlar sözlüğünü oluştur
        oranlar = {}
        for _, row in oranlar_df.iterrows():
            oranlar[row["Hesap İsmi"]] = {
                "osgb": row["OSGB"],
                "belge": row["BELGE"],
                "alt": {
                    "egitim": row["Eğitim"],
                    "ilkyardim": row["İlk Yardım"],
                    "kalite": row["Kalite"],
                    "uzmanlik": row["Uzmanlık"]
                }
            }

        sonuc = []
        for _, row in df.iterrows():
            hesap = row["Hesap İsmi"]
            sorumluluk = row["SORUMLULUK MERKEZİ İSMİ"]
            tutar = row["Tutar"]

            bas = pd.to_datetime(row["Başlangıç"] + " 2025", format="%B %Y")
            bit = pd.to_datetime(row["Bitiş"] + " 2025", format="%B %Y")
            ay_listesi = pd.date_range(bas, bit, freq="MS")
            oran = oranlar.get(hesap, None)

            if oran is None:
                st.error(f"{hesap} için oran tanımı bulunamadı!")
                continue

            if sorumluluk == "OSGB + BELGE ORTAK GİDER":
                osgb_tutar = tutar * oran["osgb"] / 100
                belge_tutar = tutar * oran["belge"] / 100
                osgb_aylik = osgb_tutar / len(ay_listesi)
                belge_aylik = belge_tutar / len(ay_listesi)
                for ay in ay_listesi:
                    sonuc.append([hesap, ay.strftime("%B"), "OSGB", osgb_aylik])
                    sonuc.append([hesap, ay.strftime("%B"), "BELGE", belge_aylik])

            elif sorumluluk == "BELGE ORTAK GİDER":
                for alt, oran_alt in oran["alt"].items():
                    alt_tutar = tutar * oran_alt / 100
                    alt_aylik = alt_tutar / len(ay_listesi)
                    for ay in ay_listesi:
                        sonuc.append([hesap, ay.strftime("%B"), alt.upper(), alt_aylik])
            else:
                aylik = tutar / len(ay_listesi)
                for ay in ay_listesi:
                    sonuc.append([hesap, ay.strftime("%B"), "DİĞER", aylik])

        sonuc_df = pd.DataFrame(sonuc, columns=["Hesap İsmi", "Ay", "Kategori", "Tutar"])
        st.subheader("Sonuç Tablosu")
        st.dataframe(sonuc_df)
