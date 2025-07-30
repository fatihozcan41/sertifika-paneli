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

# ---------------- Excel'den Yükle ----------------
if secim == "Excel'den Yükle":
    st.header("📤 Excel'den Gelir/Gider Yükleme")

    # Sıfırlama butonu
    if st.button("🗑️ Tüm Verileri Sıfırla"):
        if os.path.exists(VERI_DOSYA):
            os.remove(VERI_DOSYA)
        if os.path.exists(DOSYA_LISTESI):
            os.remove(DOSYA_LISTESI)
        st.success("Tüm veriler sıfırlandı.")
        st.rerun()

    if not os.path.exists(DOSYA_LISTESI):
        pd.DataFrame(columns=["dosya"]).to_csv(DOSYA_LISTESI, index=False)

    # Mevcut yüklenen dosyaları göster
    dosya_listesi = pd.read_csv(DOSYA_LISTESI)
    if not dosya_listesi.empty:
        st.subheader("📂 Yüklenen Dosyalar")
        for i, row in dosya_listesi.iterrows():
            col1, col2, col3 = st.columns([4, 1, 1])
            col1.write(row["dosya"])

            # Sil butonu
            if col2.button("❌ Sil", key=f"sil_{i}"):
                dosya_listesi = dosya_listesi.drop(i)
                dosya_listesi.to_csv(DOSYA_LISTESI, index=False)
                if os.path.exists(VERI_DOSYA):
                    veri_df = pd.read_csv(VERI_DOSYA)
                    veri_df = veri_df[veri_df["kaynak_dosya"] != row["dosya"]]
                    veri_df.to_csv(VERI_DOSYA, index=False)
                st.rerun()

            # Değiştir butonu
            if col3.button("🔄 Değiştir", key=f"degistir_{i}"):
                st.session_state["degistirilecek_dosya"] = row["dosya"]
                st.session_state["degistirme_modu"] = True
                st.rerun()

    # Dosya değiştirme modu aktifse
    if st.session_state.get("degistirme_modu", False):
        eski_dosya = st.session_state.get("degistirilecek_dosya")
        st.subheader(f"🔄 '{eski_dosya}' dosyasını değiştir")
        col1, col2 = st.columns([3, 1])
        yeni_dosya = col1.file_uploader("Yeni dosyayı seçin", type=["xlsx", "xls"], key="degistirme")
        if col2.button("Vazgeç"):
            st.session_state["degistirme_modu"] = False
            st.rerun()
        if yeni_dosya:
            dosya_listesi = dosya_listesi[dosya_listesi["dosya"] != eski_dosya]
            dosya_listesi = pd.concat(
                [dosya_listesi, pd.DataFrame([[yeni_dosya.name]], columns=["dosya"])],
                ignore_index=True
            )
            dosya_listesi.to_csv(DOSYA_LISTESI, index=False)

            veri_df = pd.read_csv(VERI_DOSYA)
            eski_kayitlar = veri_df[veri_df["kaynak_dosya"] == eski_dosya]

            # Eski dosyanın bilgileri
            firma_bilgi = eski_kayitlar["firma"].iloc[0] if not eski_kayitlar.empty else "Etki OSGB"
            ay_bilgi = eski_kayitlar["ay"].iloc[0] if not eski_kayitlar.empty else "Haziran"
            tur_bilgi = eski_kayitlar["tur"].iloc[0] if not eski_kayitlar.empty else "Gider"

            veri_df = veri_df[veri_df["kaynak_dosya"] != eski_dosya]
            yeni_df = pd.read_excel(yeni_dosya)
            bas_col = "Gider Başlangıç" if "Gider Başlangıç" in yeni_df.columns else "Başlangıç"
            bit_col = "Gider Bitiş Tarihi" if "Gider Bitiş Tarihi" in yeni_df.columns else "Bitiş"

            for _, r in yeni_df.iterrows():
                yeni_kayit = {
                    "firma": firma_bilgi,
                    "ay": ay_bilgi,
                    "tur": tur_bilgi,
                    "HESAP İSMİ": r["HESAP İSMİ"],
                    "ANA DÖVİZ BORÇ": r["ANA DÖVİZ BORÇ"],
                    "SORUMLULUK MERKEZİ İSMİ": r["SORUMLULUK MERKEZİ İSMİ"],
                    "bas": r[bas_col] if bas_col in yeni_df.columns else None,
                    "bit": r[bit_col] if bit_col in yeni_df.columns else None,
                    "kaynak_dosya": yeni_dosya.name
                }
                veri_df = pd.concat([veri_df, pd.DataFrame([yeni_kayit])], ignore_index=True)

            veri_df.to_csv(VERI_DOSYA, index=False)
            st.session_state["degistirme_modu"] = False
            st.success("Dosya başarıyla değiştirildi ve tablolar güncellendi.")
            st.rerun()

    yuklenecek_firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
    secilen_ay = st.selectbox("Hangi Ay İçin?", aylar)
    yuklenecek_tur = st.selectbox("Gider mi Gelir mi?", ["Gider", "Gelir"])
    excel_dosyasi = st.file_uploader("Excel Dosyasını Seçin", type=["xlsx", "xls"], key="yeni_yukleme")

    if not os.path.exists(VERI_DOSYA):
        pd.DataFrame(
            columns=["firma", "ay", "tur", "HESAP İSMİ", "ANA DÖVİZ BORÇ",
                     "SORUMLULUK MERKEZİ İSMİ", "bas", "bit", "kaynak_dosya"]
        ).to_csv(VERI_DOSYA, index=False)

    if excel_dosyasi:
        if excel_dosyasi.name not in list(dosya_listesi["dosya"]):
            yeni_df = pd.read_excel(excel_dosyasi)
            bas_col = "Gider Başlangıç" if "Gider Başlangıç" in yeni_df.columns else "Başlangıç"
            bit_col = "Gider Bitiş Tarihi" if "Gider Bitiş Tarihi" in yeni_df.columns else "Bitiş"

            mevcut_df = pd.read_csv(VERI_DOSYA)
            for _, row in yeni_df.iterrows():
                hesap_ismi = row["HESAP İSMİ"]
                mevcut_df = mevcut_df[~(
                    (mevcut_df["firma"] == yuklenecek_firma) &
                    (mevcut_df["ay"] == secilen_ay) &
                    (mevcut_df["HESAP İSMİ"] == hesap_ismi)
                )]
                yeni_kayit = {
                    "firma": yuklenecek_firma,
                    "ay": secilen_ay,
                    "tur": yuklenecek_tur,
                    "HESAP İSMİ": hesap_ismi,
                    "ANA DÖVİZ BORÇ": row["ANA DÖVİZ BORÇ"],
                    "SORUMLULUK MERKEZİ İSMİ": row["SORUMLULUK MERKEZİ İSMİ"],
                    "bas": row[bas_col] if bas_col in yeni_df.columns else None,
                    "bit": row[bit_col] if bit_col in yeni_df.columns else None,
                    "kaynak_dosya": excel_dosyasi.name
                }
                mevcut_df = pd.concat([mevcut_df, pd.DataFrame([yeni_kayit])], ignore_index=True)

            mevcut_df.to_csv(VERI_DOSYA, index=False)
            dosya_listesi = pd.concat(
                [dosya_listesi, pd.DataFrame([[excel_dosyasi.name]], columns=["dosya"])],
                ignore_index=True
            )
            dosya_listesi.to_csv(DOSYA_LISTESI, index=False)
            st.success(f"✅ {excel_dosyasi.name} yüklendi ve tablolar güncellendi.")
            st.rerun()
        else:
            st.warning("Bu dosya zaten yüklenmiş. İsterseniz listeden silip tekrar yükleyin.")

    # Ay Bazlı Dağılım tabloları göster
    if os.path.exists(VERI_DOSYA):
        tum_df = pd.read_csv(VERI_DOSYA)
        osgb_dagilim = []
        belge_dagilim = []

        for _, row in tum_df.iterrows():
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
                        for ao in ["egitim", "ilkyardim", "kalite", "uzmanlik"]:
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
