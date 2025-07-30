import streamlit as st
import pandas as pd
import os

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

secim = st.selectbox("Modül Seçiniz", ["Excel'den Yükle", "Oran Tanımla"])

# ---------------- Excel'den Yükle ----------------
if secim == "Excel'den Yükle":
    st.header("📤 Excel'den Gelir/Gider Yükleme")
    yuklenecek_firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
    excel_dosyasi = st.file_uploader("Excel Dosyasını Seçin", type=["xlsx","xls"])

    if excel_dosyasi:
        df = pd.read_excel(excel_dosyasi)

        bas_col = "Gider Başlangıç" if "Gider Başlangıç" in df.columns else "Başlangıç"
        bit_col = "Gider Bitiş Tarihi" if "Gider Bitiş Tarihi" in df.columns else "Bitiş"

        if bas_col not in df.columns or bit_col not in df.columns:
            st.error("Başlangıç ve Bitiş sütunları bulunamadı.")
        else:
            df[bas_col] = pd.to_datetime(df[bas_col])
            df[bit_col] = pd.to_datetime(df[bit_col])

            osgb_dagilim = []
            belge_dagilim = []

            for _, row in df.iterrows():
                hesap = row["HESAP İSMİ"]
                sorumluluk = str(row["SORUMLULUK MERKEZİ İSMİ"]).upper().strip()
                toplam_tutar = row["ANA DÖVİZ BORÇ"]
                bas = row[bas_col]
                bit = row[bit_col]
                ay_sayisi = (bit.to_period('M') - bas.to_period('M')).n + 1
                tutar_aylik = toplam_tutar / ay_sayisi if ay_sayisi > 0 else toplam_tutar

                oran = oran_bul(hesap)

                for i in range(ay_sayisi):
                    ay_adi = aylar[(bas + pd.DateOffset(months=i)).month - 1]

                    if yuklenecek_firma == "Etki OSGB":
                        if sorumluluk == "OSGB + BELGE ORTAK GİDER" and oran is not None:
                            osgb_dagilim.append((hesap, ay_adi, tutar_aylik * oran["osgb"] / 100))
                            belge_dagilim.append((hesap, ay_adi, tutar_aylik * oran["belge"] / 100))
                        else:
                            osgb_dagilim.append((hesap, ay_adi, tutar_aylik))

                    elif yuklenecek_firma == "Etki Belgelendirme":
                        if sorumluluk == "OSGB + BELGE ORTAK GİDER" and oran is not None:
                            osgb_dagilim.append((hesap, ay_adi, tutar_aylik * oran["osgb"] / 100))
                            belge_dagilim.append((hesap, ay_adi, tutar_aylik * oran["belge"] / 100))
                        elif sorumluluk == "BELGE ORTAK GİDER" and oran is not None:
                            for ao in ["egitim","ilkyardim","kalite","uzmanlik"]:
                                alt_tutar = tutar_aylik * (oran[ao] / oran["belge"]) if oran["belge"] > 0 else 0
                                belge_dagilim.append((f"{hesap}-{ao.upper()}", ay_adi, alt_tutar))
                        else:
                            belge_dagilim.append((hesap, ay_adi, tutar_aylik))

            def pivot_tablo(data):
                df = pd.DataFrame(data, columns=["HESAP İSMİ", "Ay", "Tutar"])
                if df.empty:
                    return pd.DataFrame(columns=["HESAP İSMİ"] + aylar)
                pivot = df.pivot_table(index="HESAP İSMİ", columns="Ay", values="Tutar", aggfunc="sum").reset_index()
                for ay in aylar:
                    if ay not in pivot.columns:
                        pivot[ay] = 0
                return pivot[["HESAP İSMİ"] + aylar]

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
