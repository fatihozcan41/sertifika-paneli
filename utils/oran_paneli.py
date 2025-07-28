
import streamlit as st
import pandas as pd

def oran_giris_paneli(df, firma_adi):
    st.subheader("Oran Giriş Paneli")
    unique_hesaplar = df["HESAP İSMİ"].dropna().unique()
    oranlar = []
    for hesap in unique_hesaplar:
        st.markdown(f"**{hesap}**")
        osgb_orani = st.slider(f"{hesap} - Etki OSGB (%)", 0, 100, 100 if firma_adi == "Etki OSGB" else 0)
        belgelendirme_orani = 100 - osgb_orani
        egitim = ilkyardim = kalite = uzman = 0
        if belgelendirme_orani > 0 and firma_adi == "Etki Belgelendirme":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                egitim = st.slider(f"{hesap} - Eğitim (%)", 0, 100, 25)
            with col2:
                ilkyardim = st.slider(f"{hesap} - İlkyardım (%)", 0, 100, 25)
            with col3:
                kalite = st.slider(f"{hesap} - Kalite (%)", 0, 100, 25)
            with col4:
                uzman = st.slider(f"{hesap} - Uzman (%)", 0, 100, 25)
        oranlar.append({
            "HESAP İSMİ": hesap,
            "Etki OSGB": osgb_orani,
            "Etki Belgelendirme": belgelendirme_orani,
            "Eğitim": egitim,
            "İlkyardım": ilkyardim,
            "Kalite": kalite,
            "Uzman": uzman
        })
    return pd.DataFrame(oranlar)
