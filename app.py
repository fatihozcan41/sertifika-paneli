import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

VERI_DOSYA = "data/veriler.csv"
ORAN_DOSYA = "data/oranlar.csv"

aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]

def oran_bul(h_ismi):
    if not os.path.exists(ORAN_DOSYA):
        return None
    oran_df = pd.read_csv(ORAN_DOSYA)
    row = oran_df[oran_df["hesap_ismi"] == h_ismi]
    return row.iloc[0] if not row.empty else None

st.set_page_config(page_title="Etki Gelir Gider Takip", layout="wide")
st.title("📘 Etki OSGB & Etki Belgelendirme Gelir-Gider Takip Paneli")

secim = st.selectbox("Nasıl devam etmek istersiniz?", ["Manuel Veri Girişi", "Excel'den Yükle", "Oran Tanımla", "Raporlama"])

# -------------------- Excel Yükleme --------------------
if secim == "Excel'den Yükle":
    st.header("📤 Excel'den Gelir/Gider Yükleme")
    with st.form("excel_upload"):
        yuklenecek_firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
        yuklenecek_tur = st.radio("İşlem Türü", ["Gelir", "Gider"])
        yuklenecek_ay = st.selectbox("Ay", aylar)
        excel_dosyasi = st.file_uploader("Excel Dosyasını Yükleyin", type=["xlsx","xls"])
        yukle_btn = st.form_submit_button("Verileri Aktar")

        if yukle_btn and excel_dosyasi:
            try:
                yuklenen_df = pd.read_excel(excel_dosyasi)

                if not all(k in yuklenen_df.columns for k in ["HESAP İSMİ","ANA DÖVİZ BORÇ","SORUMLULUK MERKEZİ İSMİ"]):
                    st.error("❌ Excel dosyası gerekli sütunlara sahip değil.")
                else:
                    bas_col = "Gider Başlangıç" if "Gider Başlangıç" in yuklenen_df.columns else "Başlangıç"
                    bit_col = "Gider Bitiş Tarihi" if "Gider Bitiş Tarihi" in yuklenen_df.columns else "Bitiş"
                    
                    if bas_col not in yuklenen_df.columns or bit_col not in yuklenen_df.columns:
                        st.error("Excel'de Başlangıç ve Bitiş tarihleri bulunamadı.")
                    else:
                        yuklenen_df[bas_col] = pd.to_datetime(yuklenen_df[bas_col])
                        yuklenen_df[bit_col] = pd.to_datetime(yuklenen_df[bit_col])

                        osgb_dagilim = []
                        belge_dagilim = []

                        for _, row in yuklenen_df.iterrows():
                            hesap_ismi = row["HESAP İSMİ"]
                            sorumluluk = str(row["SORUMLULUK MERKEZİ İSMİ"]).upper().strip()
                            tutar_toplam = row["ANA DÖVİZ BORÇ"]
                            bas = row[bas_col]
                            bit = row[bit_col]
                            toplam_ay = (bit.to_period('M') - bas.to_period('M')).n + 1
                            tutar_aylik = tutar_toplam / toplam_ay if toplam_ay > 0 else tutar_toplam

                            oran = oran_bul(hesap_ismi)

                            for i in range(toplam_ay):
                                ay = (bas + pd.DateOffset(months=i)).month
                                ay_adi = aylar[ay-1]

                                if yuklenecek_firma == "Etki OSGB":
                                    if sorumluluk == "OSGB + BELGE ORTAK GİDER" and oran is not None:
                                        osgb_dagilim.append((hesap_ismi, ay_adi, tutar_aylik * oran["osgb"] / 100))
                                        belge_dagilim.append((hesap_ismi, ay_adi, tutar_aylik * oran["belge"] / 100))
                                    else:
                                        osgb_dagilim.append((hesap_ismi, ay_adi, tutar_aylik))

                                elif yuklenecek_firma == "Etki Belgelendirme":
                                    if sorumluluk == "OSGB + BELGE ORTAK GİDER" and oran is not None:
                                        osgb_dagilim.append((hesap_ismi, ay_adi, tutar_aylik * oran["osgb"] / 100))
                                        belge_dagilim.append((hesap_ismi, ay_adi, tutar_aylik * oran["belge"] / 100))
                                    elif sorumluluk == "BELGE ORTAK GİDER" and oran is not None:
                                        alt_oranlar = ["egitim","ilkyardim","kalite","uzmanlik"]
                                        for ao in alt_oranlar:
                                            alt_tutar = tutar_aylik * (oran[ao] / oran["belge"]) if oran["belge"] > 0 else 0
                                            belge_dagilim.append((f"{{hesap_ismi}}-{{ao.upper()}}", ay_adi, alt_tutar))
                                    else:
                                        belge_dagilim.append((hesap_ismi, ay_adi, tutar_aylik))

                        def pivot_tablo(dagilim_listesi):
                            df = pd.DataFrame(dagilim_listesi, columns=["HESAP İSMİ","Ay","Tutar"])
                            if df.empty:
                                return pd.DataFrame(columns=["HESAP İSMİ"] + aylar)
                            pivot = df.pivot_table(index="HESAP İSMİ", columns="Ay", values="Tutar", aggfunc="sum").reset_index()
                            for ay in aylar:
                                if ay not in pivot.columns:
                                    pivot[ay] = 0
                            return pivot[["HESAP İSMİ"] + aylar]

                        osgb_df = pivot_tablo(osgb_dagilim)
                        belge_df = pivot_tablo(belge_dagilim)

                        st.markdown("### 🟢 Etki OSGB Ay Bazlı Dağılım Tablosu")
                        st.dataframe(osgb_df, use_container_width=True)

                        st.markdown("### 🔵 Etki Belgelendirme Ay Bazlı Dağılım Tablosu")
                        st.dataframe(belge_df, use_container_width=True)

            except Exception as e:
                st.error(f"Hata oluştu: {{e}}")
