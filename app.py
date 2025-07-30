import streamlit as st
import pandas as pd
import os

ORAN_DOSYA = "data/oranlar.csv"
VERI_DOSYA = "data/yuklenen_veriler.csv"
DOSYA_LISTESI = "data/yuklenen_dosyalar.csv"
aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]

def oran_bul(h_ismi):
    if not os.path.exists(ORAN_DOSYA):
        return None
    oran_df = pd.read_csv(ORAN_DOSYA)
    row = oran_df[oran_df["hesap_ismi"] == h_ismi]
    return row.iloc[0] if not row.empty else None

def pivot_tablo(data):
    df = pd.DataFrame(data, columns=["HESAP İSMİ", "Ay", "Tutar"])
    if df.empty:
        return pd.DataFrame(columns=["HESAP İSMİ"] + aylar)
    pivot = df.pivot_table(index="HESAP İSMİ", columns="Ay", values="Tutar", aggfunc="sum").reset_index()
    for ay in aylar:
        if ay not in pivot.columns:
            pivot[ay] = 0
    pivot = pivot.fillna(0)
    return pivot[["HESAP İSMİ"] + aylar]

st.set_page_config(page_title="Etki Gelir Gider Takip", layout="wide")
st.title("📘 Etki OSGB & Etki Belgelendirme Gelir-Gider Takip Paneli")

secim = st.selectbox("Modül Seçiniz", ["Excel'den Yükle", "Oran Tanımla"])

if secim == "Excel'den Yükle":
    st.header("📤 Excel'den Gelir/Gider Yükleme")

    if os.path.exists(VERI_DOSYA):
        tum_df = pd.read_csv(VERI_DOSYA)
        osgb_dagilim = []
        belge_dagilim = []

        for _, row in tum_df.iterrows():
            hesap = row["HESAP İSMİ"]
            sorumluluk = str(row["SORUMLULUK MERKEZİ İSMİ"]).upper().strip()
            toplam_tutar = row["ANA DÖVİZ BORÇ"]

            # Başlangıç ve bitiş tarihlerini kontrol et
            bas = None
            bit = None
            try:
                if pd.notna(row["bas"]):
                    bas = pd.to_datetime(row["bas"])
            except Exception:
                bas = None

            try:
                if pd.notna(row["bit"]):
                    bit = pd.to_datetime(row["bit"])
            except Exception:
                bit = None

            # Ay listesi oluştur
            if bas is not None and bit is not None:
                ay_sayisi = (bit.to_period('M') - bas.to_period('M')).n + 1
                ay_listesi = [(bas + pd.DateOffset(months=i)).month for i in range(ay_sayisi)]
            else:
                st.warning(f"⚠️ {hesap} için Başlangıç/Bitiş tarihi hatalı veya boş, seçilen aya yazıldı.")
                ay_listesi = [aylar.index(row["ay"]) + 1]

            # Tutarı ay sayısına böl
            tutar_aylik = toplam_tutar / len(ay_listesi) if len(ay_listesi) > 0 else toplam_tutar
            oran = oran_bul(hesap)

            for ay_no in ay_listesi:
                ay_adi = aylar[ay_no - 1]
                if row["firma"] == "Etki OSGB":
                    if sorumluluk == "OSGB + BELGE ORTAK GİDER" and oran is not None:
                        osgb_dagilim.append((hesap, ay_adi, tutar_aylik * oran["osgb"] / 100))
                        belge_dagilim.append((hesap, ay_adi, tutar_aylik * oran["belge"] / 100))
                    else:
                        osgb_dagilim.append((hesap, ay_adi, tutar_aylik))
                elif row["firma"] == "Etki Belgelendirme":
                    if sorumluluk == "OSGB + BELGE ORTAK GİDER" and oran is not None:
                        osgb_dagilim.append((hesap, ay_adi, tutar_aylik * oran["osgb"] / 100))
                        belge_dagilim.append((hesap, ay_adi, tutar_aylik * oran["belge"] / 100))
                    elif sorumluluk == "BELGE ORTAK GİDER" and oran is not None:
                        for ao in ["egitim","ilkyardim","kalite","uzmanlik"]:
                            alt_tutar = tutar_aylik * (oran[ao] / oran["belge"]) if oran["belge"] > 0 else 0
                            belge_dagilim.append((f"{hesap}-{ao.upper()}", ay_adi, alt_tutar))
                    else:
                        belge_dagilim.append((hesap, ay_adi, tutar_aylik))

        st.subheader("🟢 Etki OSGB Ay Bazlı Dağılım")
        st.dataframe(pivot_tablo(osgb_dagilim), use_container_width=True)

        st.subheader("🔵 Etki Belgelendirme Ay Bazlı Dağılım")
        st.dataframe(pivot_tablo(belge_dagilim), use_container_width=True)
