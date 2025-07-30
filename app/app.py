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

    # Verileri sıfırlama butonu
    if st.button("🗑️ Tüm Verileri Sıfırla"):
        if os.path.exists(VERI_DOSYA):
            os.remove(VERI_DOSYA)
        if os.path.exists(DOSYA_LISTESI):
            os.remove(DOSYA_LISTESI)
        st.success("Tüm veriler sıfırlandı.")
        st.rerun()

    # Yüklenen dosyalar listesi
    if not os.path.exists(DOSYA_LISTESI):
        pd.DataFrame(columns=["dosya"]).to_csv(DOSYA_LISTESI, index=False)

    dosya_listesi = pd.read_csv(DOSYA_LISTESI)
    if not dosya_listesi.empty:
        st.subheader("📂 Yüklenen Dosyalar")
        for i, row in dosya_listesi.iterrows():
            col1, col2, col3 = st.columns([4,1,1])
            col1.write(row["dosya"])
            if col2.button("❌ Sil", key=f"sil_{i}"):
                dosya_listesi = dosya_listesi.drop(i)
                dosya_listesi.to_csv(DOSYA_LISTESI, index=False)
                if os.path.exists(VERI_DOSYA):
                    veri_df = pd.read_csv(VERI_DOSYA)
                    veri_df = veri_df[veri_df["kaynak_dosya"] != row["dosya"]]
                    veri_df.to_csv(VERI_DOSYA, index=False)
                st.rerun()
            if col3.button("🔄 Değiştir", key=f"degistir_{i}"):
                st.session_state["degistirilecek_dosya"] = row["dosya"]
                st.session_state["degistirme_modu"] = True
                st.rerun()

    # Değiştirme modu
    if st.session_state.get("degistirme_modu", False):
        eski_dosya = st.session_state.get("degistirilecek_dosya")
        st.subheader(f"🔄 '{eski_dosya}' dosyasını değiştir")
        col1, col2 = st.columns([3,1])
        yeni_dosya = col1.file_uploader("Yeni dosyayı seçin", type=["xlsx","xls"], key="degistirme")
        if col2.button("Vazgeç"):
            st.session_state["degistirme_modu"] = False
            st.rerun()
        if yeni_dosya:
            # Eski kayıtları temizle ve yeni dosya ekle
            dosya_listesi = dosya_listesi[dosya_listesi["dosya"] != eski_dosya]
            dosya_listesi = pd.concat([dosya_listesi, pd.DataFrame([[yeni_dosya.name]], columns=["dosya"])], ignore_index=True)
            dosya_listesi.to_csv(DOSYA_LISTESI, index=False)
            veri_df = pd.read_csv(VERI_DOSYA)
            veri_df = veri_df[veri_df["kaynak_dosya"] != eski_dosya]
            yeni_df = pd.read_excel(yeni_dosya)
            for _, r in yeni_df.iterrows():
                veri_df = pd.concat([veri_df, pd.DataFrame([r])], ignore_index=True)
            veri_df.to_csv(VERI_DOSYA, index=False)
            st.session_state["degistirme_modu"] = False
            st.success("Dosya değiştirildi.")
            st.rerun()

    # Firma, ay ve Gider/Gelir seçimi
    yuklenecek_firma = st.selectbox("Firma", ["Etki OSGB", "Etki Belgelendirme"])
    secilen_ay = st.selectbox("Hangi Ay İçin?", aylar)
    yuklenecek_tur = st.selectbox("Gider mi Gelir mi?", ["Gider", "Gelir"])

    if os.path.exists(VERI_DOSYA):
        tum_df = pd.read_csv(VERI_DOSYA)
        osgb_dagilim = []
        belge_dagilim = []

        for _, row in tum_df.iterrows():
            hesap = row["HESAP İSMİ"]
            sorumluluk = str(row["SORUMLULUK MERKEZİ İSMİ"]).upper().strip()
            toplam_tutar = row["ANA DÖVİZ BORÇ"]

            # Tarih kontrolü
            bas, bit = None, None
            try:
                if pd.notna(row["bas"]):
                    bas = pd.to_datetime(row["bas"])
            except:
                bas = None

            try:
                if pd.notna(row["bit"]):
                    bit = pd.to_datetime(row["bit"])
            except:
                bit = None

            # Ay listesi
            if bas is not None and bit is not None:
                ay_sayisi = (bit.to_period('M') - bas.to_period('M')).n + 1
                ay_listesi = [(bas + pd.DateOffset(months=i)).month for i in range(ay_sayisi)]
            else:
                st.warning(f"⚠️ {hesap} için tarih hatalı veya boş, seçilen aya yazıldı.")
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
