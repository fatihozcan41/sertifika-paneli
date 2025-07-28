import streamlit as st

st.set_page_config(page_title="Etki Bütçe Takip", layout="wide")

st.title("📊 Etki OSGB & Belgelendirme Bütçe Takip Sistemi")

# Firma seçimi
firma = st.selectbox("Firma Seçiniz", ["Etki OSGB", "Etki Belgelendirme"])

# Tür seçimi
tur = st.radio("İşlem Türü", ["Gelir", "Gider"], horizontal=True)

# Ay seçimi
ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])

# Diğer bilgiler
hesap_ismi = st.text_input("Hesap İsmi")
tutar = st.number_input("Tutar (₺)", min_value=0.0, format="%.2f")
sorumluluk = st.text_input("Sorumluluk Merkezi")
tarih = st.date_input("Tarih")

if st.button("Veriyi Kaydet"):
    st.success("Veri başarıyla kaydedildi (örnek).")

st.markdown("---")
st.subheader("🧮 Oran Tanımlama")

hesap_oran_ismi = st.text_input("Oran için HESAP İSMİ", key="oranhesap")

col1, col2 = st.columns(2)
with col1:
    osgb_oran = st.number_input("Etki OSGB (%)", min_value=0, max_value=100, value=40)
with col2:
    belge_oran = st.number_input("Etki Belgelendirme (%)", min_value=0, max_value=100, value=60)

st.caption("Aşağıdaki oranlar yalnızca Etki Belgelendirme oranı içindir:")
col3, col4 = st.columns(2)
with col3:
    egitim = st.number_input("EĞİTİM (%)", min_value=0, max_value=100, value=25)
    kalite = st.number_input("KALİTE DANIŞMANLIK (%)", min_value=0, max_value=100, value=30)
with col4:
    ilkyardim = st.number_input("İLKYARDIM (%)", min_value=0, max_value=100, value=25)
    uzmanlik = st.number_input("UZMANLIK (%)", min_value=0, max_value=100, value=20)

if st.button("Oranları Kaydet"):
    if osgb_oran + belge_oran != 100:
        st.error("OSGB ve Belgelendirme toplamı %100 olmalı!")
    elif egitim + ilkyardim + kalite + uzmanlik != 100:
        st.error("Belgelendirme alt dağılım oranları toplamı %100 olmalı!")
    elif not hesap_oran_ismi:
        st.error("Hesap ismi giriniz.")
    else:
        st.success(f"'{hesap_oran_ismi}' için oranlar başarıyla kaydedildi (örnek).")
