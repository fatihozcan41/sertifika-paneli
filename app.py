import streamlit as st
import pandas as pd
import os

ORAN_DOSYA = "data/oranlar.csv"
VERI_DOSYA = "data/yuklenen_veriler.csv"
aylar = ["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran","Temmuz","Ağustos","Eylül","Ekim","Kasım","Aralık"]


# ---------------- Eksik Oran Kontrolü ----------------
def kontrol_oranlar_yukleme(df):
    eksik_listesi = []
    for idx, row in df.iterrows():
        sorumluluk = str(row.get("SORUMLULUK MERKEZİ İSMİ", "")).strip()
        hesap = str(row.get("HESAP İSMİ", "")).strip()
        
if ay_listesi and len(ay_listesi) > 0:
    tutar_aylik = toplam_tutar / len(ay_listesi)
else:
    st.warning("⚠️ Başlangıç ve Bitiş aralığında ay bulunamadı. Tutar tek seferde listelendi.")
    tutar_aylik = toplam_tutar
else:
    st.warning("⚠️ Başlangıç ve Bitiş aralığında ay bulunamadı. Tutar tek seferde listelendi.")
    tutar_aylik = toplam_tutar
            else:
                tutar_aylik = tutar
            for ay in ay_listesi:
                firma = "Etki OSGB" 
if ay_listesi and len(ay_listesi) > 0:
    tutar_aylik = toplam_tutar / len(ay_listesi)
else:
    st.warning("⚠️ Başlangıç ve Bitiş aralığında ay bulunamadı. Tutar tek seferde listelendi.")
    tutar_aylik = toplam_tutar
else:
    st.warning("⚠️ Başlangıç ve Bitiş aralığında ay bulunamadı. Tutar tek seferde listelendi.")
    tutar_aylik = toplam_tutar
else:
    st.warning("⚠️ Başlangıç ve Bitiş arasında ay bulunamadı. Tutar tek seferde listelendi.")
    tutar_aylik = toplam_tutar
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

# ---------------- Oran Tanımlama ----------------
elif secim == "Oran Tanımla":
    st.header("⚙️ Oran Tanımlama")
    oran_df = pd.read_csv(ORAN_DOSYA)
    edit = st.data_editor(oran_df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Kaydet"):
        hatalar = []
        for idx, row in edit.iterrows():
            osgb = float(row.get("osgb", 0) or 0)
            belge = float(row.get("belge", 0) or 0)
            toplam_alt = float(row.get("egitim", 0) or 0) + float(row.get("ilkyardim", 0) or 0) + float(row.get("kalite", 0) or 0) + float(row.get("uzmanlik", 0) or 0)
            if abs(osgb + belge - 100) > 0.001:
                hatalar.append(f"Satır {idx+1}: OSGB + Belge toplamı 100 olmalı.")
            if abs(toplam_alt - belge) > 0.001:
                hatalar.append(f"Satır {idx+1}: Alt dağılım toplamı Belge oranına eşit olmalı.")

        if hatalar:
            for h in hatalar:
                st.error(h)
        else:
            edit.to_csv(ORAN_DOSYA, index=False)
            st.success("Oranlar kaydedildi.")


def dagit_osgb_belge(hesap, tutar, oran, bas_tarih, bit_tarih):
    """OSGB + BELGE ORTAK GİDER tutarını oranlara göre ay bazlı dağıtır."""
    ay_sayisi = (bit_tarih.year - bas_tarih.year) * 12 + (bit_tarih.month - bas_tarih.month) + 1

    osgb_tutar = tutar * oran["osgb"] / 100
    belge_tutar = tutar * oran["belge"] / 100

    if ay_sayisi > 0:
        osgb_aylik = osgb_tutar / ay_sayisi
        belge_aylik = belge_tutar / ay_sayisi
    else:
        st.warning("⚠️ Başlangıç-Bitiş aralığında ay bulunamadı. Tutarlar tek seferde dağıtıldı.")
        osgb_aylik = osgb_tutar
        belge_aylik = belge_tutar

    return osgb_aylik, belge_aylik, ay_sayisi


def dagit_belge_alt(hesap, tutar, oran, bas_tarih, bit_tarih):
    """BELGE ORTAK GİDER tutarını alt kırılımlara göre ay bazlı dağıtır."""
    ay_sayisi = (bit_tarih.year - bas_tarih.year) * 12 + (bit_tarih.month - bas_tarih.month) + 1
    belge_alt = {}

    for ao in ["egitim", "ilkyardim", "kalite", "uzmanlik"]:
        if oran["belge"] > 0:
            alt_tutar = tutar * (oran[ao] / oran["belge"])
        else:
            alt_tutar = 0

        if ay_sayisi > 0:
            belge_alt[ao] = alt_tutar / ay_sayisi
        else:
            st.warning(f"⚠️ Başlangıç-Bitiş aralığında ay bulunamadı ({ao}). Tek seferde dağıtıldı.")
            belge_alt[ao] = alt_tutar

    return belge_alt, ay_sayisi
