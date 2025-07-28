
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
