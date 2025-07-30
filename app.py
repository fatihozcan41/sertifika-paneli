import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

VERI_DOSYA = "data/veriler.csv"
ORAN_DOSYA = "data/oranlar.csv"

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

                    mevcut_df = pd.read_csv(VERI_DOSYA)
                    birlesmis = pd.concat([mevcut_df, aktarim_df], ignore_index=True)
                    birlesmis.to_csv(VERI_DOSYA, index=False)
                    st.success("✅ Excel verileri başarıyla aktarıldı.")

                    # --- Ay Bazlı Dağılım Tablosu ---
                    if "Gider Başlangıç" in yuklenen_df.columns and "Gider Bitiş Tarihi" in yuklenen_df.columns:
                        try:
                            yuklenen_df["Gider Başlangıç"] = pd.to_datetime(yuklenen_df["Gider Başlangıç"])
                            yuklenen_df["Gider Bitiş Tarihi"] = pd.to_datetime(yuklenen_df["Gider Bitiş Tarihi"])
                            aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]
                            
                            dagilim_listesi = []
                            for _, row in yuklenen_df.iterrows():
                                bas = row["Gider Başlangıç"]
                                bit = row["Gider Bitiş Tarihi"]
                                toplam_ay = (bit.to_period('M') - bas.to_period('M')).n + 1
                                tutar = row["ANA DÖVİZ BORÇ"] / toplam_ay if toplam_ay > 0 else row["ANA DÖVİZ BORÇ"]
                                
                                dagilim = { "HESAP İSMİ": row["HESAP İSMİ"] }
                                for i in range(toplam_ay):
                                    ay = (bas + pd.DateOffset(months=i)).month
                                    ay_adi = aylar[ay-1]
                                    dagilim[ay_adi] = tutar
                                dagilim_listesi.append(dagilim)
                            
                            dagilim_df = pd.DataFrame(dagilim_listesi).fillna(0)
                            st.markdown("### 📊 Ay Bazlı Dağılım Tablosu")
                            st.dataframe(dagilim_df, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Ay bazlı dağılım tablosu oluşturulamadı: {e}")
                    else:
                        st.info("Excel dosyasında 'Gider Başlangıç' ve 'Gider Bitiş Tarihi' kolonları bulunamadı.")
            except Exception as e:
                st.error(f"Hata oluştu: {e}")

# -------------------- Oran Tanımlama --------------------
elif secim == "Oran Tanımla":
    st.header("⚙️ Oran Tanımlama Paneli")
    oranlar_df = pd.read_csv(ORAN_DOSYA)

    st.subheader("📝 Mevcut Oranları Düzenle / Yeni Ekle veya Sil")
    edited_df = st.data_editor(oranlar_df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Değişiklikleri Kaydet"):
        hatali_satirlar = []
        for idx, row in edited_df.iterrows():
            osgb = float(row.get('osgb', 0) or 0)
            belge = float(row.get('belge', 0) or 0)
            egitim = float(row.get('egitim', 0) or 0)
            ilkyardim = float(row.get('ilkyardim', 0) or 0)
            kalite = float(row.get('kalite', 0) or 0)
            uzmanlik = float(row.get('uzmanlik', 0) or 0)

            if abs((osgb + belge) - 100) > 0.001:
                hatali_satirlar.append(f"Satır {idx+1}: OSGB + Belge toplamı 100 olmalı.")
                continue
            if abs((egitim + ilkyardim + kalite + uzmanlik) - belge) > 0.001:
                hatali_satirlar.append(f"Satır {idx+1}: Alt dağılım toplamı Belge oranına eşit olmalı.")

        if hatali_satirlar:
            for hata in hatali_satirlar:
                st.error(hata)
            st.warning("⚠️ Lütfen hatalı satırları düzeltmeden kaydetmeyin.")
        else:
            edited_df.to_csv(ORAN_DOSYA, index=False)
            st.success("Oranlar başarıyla güncellendi.")

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
