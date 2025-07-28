
import streamlit as st

st.set_page_config(page_title="Firma Bütçe Takip", layout="wide")

st.title("📊 Firma Bütçe Takip Uygulaması")
st.markdown("Veri yüklemek için sol panelden seçimleri yapınız. Aşağıdan detaylı raporlar ve analizleri görüntüleyebilirsiniz.")


# Streamlit uygulama ana dosyası



# Firma ve veri türü seçimi bölümü
with st.sidebar:
    st.header("🔧 Veri Yükleme Paneli")
    firma = st.selectbox("Firma Seçiniz", ["Etki OSGB", "Etki Belgelendirme"])
    veri_turu = st.radio("Veri Türü", ["Gider", "Gelir"])
    veri_ayi = st.selectbox("Veri Ayı", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                                         "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
    uploaded_file = st.file_uploader("Excel Dosyası Yükle", type=["xlsx"])

    if uploaded_file:
        st.success("Dosya yüklendi. İşleme hazır.")
    else:
        st.warning("Lütfen bir dosya yükleyin.")



# Oran Giriş Paneli
st.header("📊 Oran Giriş Paneli")

st.markdown("### HESAP İSMİ Bazlı Dağılım Tanımı")

hesap_ismi = st.text_input("HESAP İSMİ (örn: Elektrik Gideri)")
oran_osgb = st.slider("Etki OSGB Oranı (%)", 0, 100, 50)
oran_belgelendirme = 100 - oran_osgb

st.write(f"Etki Belgelendirme Oranı: %{oran_belgelendirme}")

if oran_belgelendirme > 0:
    st.markdown("**Etki Belgelendirme Alt Dağılımı**")
    egitim = st.slider("Eğitim (%)", 0, 100, 25)
    ilkyardim = st.slider("İlkyardım (%)", 0, 100, 25)
    kalite = st.slider("Kalite Danışmanlık (%)", 0, 100, 25)
    uzman = st.slider("Uzman Eğitim Kurumu (%)", 0, 100, 25)

    toplam = egitim + ilkyardim + kalite + uzman
    if toplam != 100:
        st.warning("Alt dağılımların toplamı %100 olmalıdır.")
    else:
        st.success("Alt dağılım oranları geçerli.")

if st.button("Oranları Kaydet"):
    st.success("Oranlar başarıyla kaydedildi. (Simülasyon)")
