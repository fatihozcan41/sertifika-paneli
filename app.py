import streamlit as st
import pandas as pd

# ----------------- Dağıtım Mantığı Fonksiyonları -----------------
def dagit_osgb_belge(hesap, tutar, oran, bas_tarih, bit_tarih):
    ay_sayisi = (bit_tarih.year - bas_tarih.year) * 12 + (bit_tarih.month - bas_tarih.month) + 1
    osgb_tutar = tutar * oran["osgb"] / 100
    belge_tutar = tutar * oran["belge"] / 100

    osgb_aylik = osgb_tutar / ay_sayisi if ay_sayisi > 0 else osgb_tutar
    belge_aylik = belge_tutar / ay_sayisi if ay_sayisi > 0 else belge_tutar

    return osgb_aylik, belge_aylik, ay_sayisi

def dagit_belge_alt(hesap, tutar, oran, bas_tarih, bit_tarih):
    ay_sayisi = (bit_tarih.year - bas_tarih.year) * 12 + (bit_tarih.month - bas_tarih.month) + 1
    belge_alt = {}
    for ao in ["egitim", "ilkyardim", "kalite", "uzmanlik"]:
        if oran["belge"] > 0:
            alt_tutar = tutar * (oran[ao] / oran["belge"])
        else:
            alt_tutar = 0
        belge_alt[ao] = alt_tutar / ay_sayisi if ay_sayisi > 0 else alt_tutar
    return belge_alt, ay_sayisi

def uygula_dagitim(df, oran_df):
    sonuc = []
    for _, row in df.iterrows():
        hesap = row["HESAP İSMİ"]
        sorumluluk = row["SORUMLULUK MERKEZİ İSMİ"]
        bas_tarih = pd.to_datetime(row["Başlangıç"])
        bit_tarih = pd.to_datetime(row["Bitiş"])
        tutar = row["TUTAR"]
        oran = oran_bul(hesap)

        if sorumluluk == "OSGB + BELGE ORTAK GİDER":
            osgb_aylik, belge_aylik, ay_sayisi = dagit_osgb_belge(hesap, tutar, oran, bas_tarih, bit_tarih)
            for i in range(ay_sayisi):
                ay = (bas_tarih + pd.DateOffset(months=i)).strftime("%Y-%m")
                sonuc.append([hesap, ay, "Etki OSGB", osgb_aylik])
                sonuc.append([hesap, ay, "Etki Belgelendirme", belge_aylik])

        elif sorumluluk == "BELGE ORTAK GİDER":
            belge_alt, ay_sayisi = dagit_belge_alt(hesap, tutar, oran, bas_tarih, bit_tarih)
            for i in range(ay_sayisi):
                ay = (bas_tarih + pd.DateOffset(months=i)).strftime("%Y-%m")
                for alt_kirilim, alt_tutar in belge_alt.items():
                    sonuc.append([hesap, ay, f"Etki Belgelendirme - {alt_kirilim}", alt_tutar])

        else:
            ay_listesi = pd.date_range(bas_tarih, bit_tarih, freq="MS")
            tutar_aylik = tutar / len(ay_listesi) if len(ay_listesi) > 0 else tutar
            for ay in ay_listesi:
                firma = "Etki OSGB" if "OSGB" in sorumluluk else "Etki Belgelendirme"
                sonuc.append([hesap, ay.strftime("%Y-%m"), firma, tutar_aylik])

    return pd.DataFrame(sonuc, columns=["HESAP İSMİ", "Ay", "Firma/Kırılım", "Tutar"])
# ------------------------------------------------------------------

import os

ORAN_DOSYA = "data/oranlar.csv"
VERI_DOSYA = "data/yuklenen_veriler.csv"
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

# ---------------- Excel'den Yükle ----------------
if secim == "Excel'den Yükle":
    st.header("📤 Excel'den Gelir/Gider Yükleme")
    yuklenecek_firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
    secilen_ay = st.selectbox("Hangi Ay İçin?", aylar)
    excel_dosyasi = st.file_uploader("Excel Dosyasını Seçin", type=["xlsx","xls"])

    if not os.path.exists(VERI_DOSYA):
        pd.DataFrame(columns=["firma","ay","HESAP İSMİ","ANA DÖVİZ BORÇ","SORUMLULUK MERKEZİ İSMİ","bas","bit"]).to_csv(VERI_DOSYA, index=False)

    if excel_dosyasi:
        yeni_df = pd.read_excel(excel_dosyasi)
        bas_col = "Gider Başlangıç" if "Gider Başlangıç" in yeni_df.columns else "Başlangıç"
        bit_col = "Gider Bitiş Tarihi" if "Gider Bitiş Tarihi" in yeni_df.columns else "Bitiş"

        mevcut_df = pd.read_csv(VERI_DOSYA)

        for _, row in yeni_df.iterrows():
            hesap_ismi = row["HESAP İSMİ"]
            # Aynı firma + ay + hesap ismi varsa eski kaydı sil
            mevcut_df = mevcut_df[~(
                (mevcut_df["firma"] == yuklenecek_firma) & 
                (mevcut_df["ay"] == secilen_ay) & 
                (mevcut_df["HESAP İSMİ"] == hesap_ismi)
            )]
            bas = row[bas_col] if bas_col in yeni_df.columns else None
            bit = row[bit_col] if bit_col in yeni_df.columns else None
            yeni_kayit = {
                "firma": yuklenecek_firma,
                "ay": secilen_ay,
                "HESAP İSMİ": hesap_ismi,
                "ANA DÖVİZ BORÇ": row["ANA DÖVİZ BORÇ"],
                "SORUMLULUK MERKEZİ İSMİ": row["SORUMLULUK MERKEZİ İSMİ"],
                "bas": bas,
                "bit": bit
            }
            mevcut_df = pd.concat([mevcut_df, pd.DataFrame([yeni_kayit])], ignore_index=True)

        mevcut_df.to_csv(VERI_DOSYA, index=False)
        st.success("✅ Dosya yüklendi ve veriler güncellendi.")

        # Ay Bazlı Dağılım otomatik göster
        osgb_dagilim = []
        belge_dagilim = []

        for _, row in mevcut_df.iterrows():
            hesap = row["HESAP İSMİ"]
            sorumluluk = str(row["SORUMLULUK MERKEZİ İSMİ"]).upper().strip()
            toplam_tutar = row["ANA DÖVİZ BORÇ"]
            bas = pd.to_datetime(row["bas"]) if pd.notna(row["bas"]) else None
            bit = pd.to_datetime(row["bit"]) if pd.notna(row["bit"]) else None

            if bas is not None and bit is not None:
                ay_sayisi = (bit.to_period('M') - bas.to_period('M')).n + 1
                ay_listesi = [(bas + pd.DateOffset(months=i)).month for i in range(ay_sayisi)]
            else:
                ay_listesi = [aylar.index(row["ay"]) + 1]

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
