import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

VERI_DOSYA = "data/veriler.csv"
ORAN_DOSYA = "data/oranlar.csv"

# Oran kontrol fonksiyonu
def oran_var_mi(h_ismi):
    if not os.path.exists(ORAN_DOSYA):
        return False
    oran_df = pd.read_csv(ORAN_DOSYA)
    return h_ismi in oran_df["hesap_ismi"].values

st.set_page_config(page_title="Etki Gelir Gider Takip", layout="wide")
st.title("📘 Etki OSGB & Etki Belgelendirme Gelir-Gider Takip Paneli")

secim = st.selectbox("Nasıl devam etmek istersiniz?", ["Manuel Veri Girişi", "Excel'den Yükle", "Oran Tanımla", "Raporlama"])

# -------------------- Manuel Veri Girişi --------------------
if secim == "Manuel Veri Girişi":
    st.header("📥 Veri Girişi")
    with st.form("manual_form"):
        firma = st.selectbox("Firma Seçiniz", ["Etki OSGB", "Etki Belgelendirme"])
        tur = st.radio("İşlem Türü", ["Gelir", "Gider"], horizontal=True)
        ay = st.selectbox("Ay", ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"])
        tarih = st.date_input("Tarih", value=date.today())
        hesap_ismi = st.text_input("Hesap İsmi")
        tutar = st.number_input("Tutar (₺)", min_value=0.0, format="%.2f")
        sorumluluk = st.text_input("Sorumluluk Merkezi")
        submitted = st.form_submit_button("Veriyi Kaydet")

        if submitted:
            if not hesap_ismi:
                st.warning("Hesap ismi girilmelidir.")
            else:
                # Oran kontrolü
                if sorumluluk.strip().upper() in ["BELGE ORTAK GİDER", "OSGB + BELGE ORTAK GİDER"] and not oran_var_mi(hesap_ismi):
                    st.warning("⚠️ Bu HESAP İSMİ için tanımlı oran bulunamadı. Lütfen oran tanımlayın.")
                yeni = pd.DataFrame([{
                    "firma": firma,
                    "tur": tur,
                    "ay": ay,
                    "tarih": tarih,
                    "hesap_ismi": hesap_ismi,
                    "tutar": tutar,
                    "sorumluluk": sorumluluk
                }])
                mevcut = pd.read_csv(VERI_DOSYA)
                df = pd.concat([mevcut, yeni], ignore_index=True)
                df.to_csv(VERI_DOSYA, index=False)
                st.success("✅ Veri kaydedildi.")

# -------------------- Excel Yükleme --------------------
elif secim == "Excel'den Yükle":
    st.header("📤 Excel'den Gelir/Gider Yükleme")
    with st.form("excel_upload"):
        yuklenecek_firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
        yuklenecek_tur = st.radio("İşlem Türü", ["Gelir", "Gider"])
        yuklenecek_ay = st.selectbox("Ay", ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"])
        excel_dosyasi = st.file_uploader("Excel Dosyasını Yükleyin", type=["xlsx","xls"])
        yukle_btn = st.form_submit_button("Verileri Aktar")

        if yukle_btn and excel_dosyasi:
            try:
                yuklenen_df = pd.read_excel(excel_dosyasi)
                beklenen_kolonlar = ["TARİH", "HESAP İSMİ", "ANA DÖVİZ BORÇ", "SORUMLULUK MERKEZİ İSMİ"]
                if not all(k in yuklenen_df.columns for k in beklenen_kolonlar):
                    st.error("❌ Excel dosyası beklenen başlıklara sahip değil.")
                else:
                    aktarim_df = pd.DataFrame({
                        "firma": yuklenecek_firma,
                        "tur": yuklenecek_tur,
                        "ay": yuklenecek_ay,
                        "tarih": yuklenen_df["TARİH"],
                        "hesap_ismi": yuklenen_df["HESAP İSMİ"],
                        "tutar": yuklenen_df["ANA DÖVİZ BORÇ"],
                        "sorumluluk": yuklenen_df["SORUMLULUK MERKEZİ İSMİ"]
                    })
                    # Oran kontrolü
                    ortak_satirlar = aktarim_df[aktarim_df["sorumluluk"].str.upper().isin(["BELGE ORTAK GİDER","OSGB + BELGE ORTAK GİDER"])]
                    oran_df = pd.read_csv(ORAN_DOSYA)
                    eksik_oranlar = ortak_satirlar[~ortak_satirlar["hesap_ismi"].isin(oran_df["hesap_ismi"])]

                    if not eksik_oranlar.empty:
                        st.warning("⚠️ Aşağıdaki HESAP İSMİ değerleri için oran tanımı yapılmamış:")
                        st.dataframe(eksik_oranlar["hesap_ismi"].unique())

                    mevcut_df = pd.read_csv(VERI_DOSYA)
                    birlesmis = pd.concat([mevcut_df, aktarim_df], ignore_index=True)
                    birlesmis.to_csv(VERI_DOSYA, index=False)
                    st.success("✅ Excel verileri başarıyla aktarıldı.")
            except Exception as e:
                st.error(f"Hata oluştu: {e}")

# -------------------- Oran Tanımlama --------------------
elif secim == "Oran Tanımla":
    st.header("⚙️ Oran Tanımlama Paneli")
    oranlar_df = pd.read_csv(ORAN_DOSYA)

    with st.form("oran_form"):
        hesap_ismi_input = st.text_input("Hesap İsmi (BELGE ORTAK GİDER veya OSGB + BELGE ORTAK GİDER altında geçen)")
        osgb_oran = st.number_input("Etki OSGB Oranı (%)", min_value=0, max_value=100, value=50)
        belge_oran = 100 - osgb_oran
        st.caption(f"Etki Belgelendirme oranı: {belge_oran}% (Alt kırılımlar toplamı {belge_oran} olmalı)")
        egitim = st.number_input("EĞİTİM (%)", min_value=0, max_value=belge_oran, value=25)
        ilkyardim = st.number_input("İLKYARDIM (%)", min_value=0, max_value=belge_oran, value=25)
        kalite = st.number_input("KALİTE (%)", min_value=0, max_value=belge_oran, value=25)
        uzmanlik = belge_oran - egitim - ilkyardim - kalite
        st.caption(f"UZMANLIK: {uzmanlik}% (Otomatik hesaplandı)")

        oran_gonder = st.form_submit_button("Oranı Kaydet")

        if oran_gonder:
            if not hesap_ismi_input:
                st.warning("Hesap ismi girilmelidir.")
            else:
                yeni_kayit = pd.DataFrame([{
                    "hesap_ismi": hesap_ismi_input,
                    "osgb": osgb_oran,
                    "belge": belge_oran,
                    "egitim": egitim,
                    "ilkyardim": ilkyardim,
                    "kalite": kalite,
                    "uzmanlik": uzmanlik
                }])
                oranlar_df = oranlar_df[oranlar_df["hesap_ismi"] != hesap_ismi_input]
                oranlar_df = pd.concat([oranlar_df, yeni_kayit], ignore_index=True)
                oranlar_df.to_csv(ORAN_DOSYA, index=False)
                st.success("✅ Oran tanımı kaydedildi.")

# -------------------- Raporlama --------------------
elif secim == "Raporlama":
    st.header("📊 Raporlama Paneli")
    if os.path.exists(VERI_DOSYA):
        df = pd.read_csv(VERI_DOSYA)
        firma_filtresi = st.multiselect("Firma", df["firma"].unique(), default=df["firma"].unique())
        ay_filtresi = st.multiselect("Ay", df["ay"].unique(), default=df["ay"].unique())
        tur_filtresi = st.multiselect("Tür", df["tur"].unique(), default=df["tur"].unique())

        filtreli = df[(df["firma"].isin(firma_filtresi)) & (df["ay"].isin(ay_filtresi)) & (df["tur"].isin(tur_filtresi))]
        toplamlar = filtreli.groupby(["firma","tur","ay"])["tutar"].sum().reset_index()
        st.dataframe(toplamlar, use_container_width=True)

        grafik = px.bar(toplamlar, x="ay", y="tutar", color="tur", barmode="group", facet_col="firma")
        st.plotly_chart(grafik, use_container_width=True)
    else:
        st.info("Henüz veri girişi yapılmamış.")
