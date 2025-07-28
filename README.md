# Firma Bütçe Takip Uygulaması

## 1. Firma Seçimi
İki firma desteklenir:
- Etki OSGB
- Etki Belgelendirme

## 2. Excel Dosyası Yükleme
Kullanıcı her ay için bir gider/gider+gelir dosyası yükler.
- Dosyada farklı sayfalar olabilir, sistem tüm sayfaları tanır.

## 3. Kullanıcıdan Alınacak Bilgiler
- Firma adı (dropdown)
- Veri türü: Gider mi, Gelir mi?
- Veri ayı (dropdown – Ocak-Aralık)
- Excel dosyasındaki aktif sayfa seçimi

## 4. Veri Formatı
Her sayfada aşağıdaki sütunlar beklenir:
- TARİH
- HESAP İSMİ
- ANA DÖVİZ BORÇ
- SORUMLULUK MERKEZİ İSMİ
- Gider Başlangıç
- Gider Bitiş Tarihi

## 5. Oran Giriş Paneli
- HESAP İSMİ bazında:
  - % Etki OSGB
  - % Etki Belgelendirme
- Etki Belgelendirme için alt kırılım:
  - % Eğitim, % İlkyardım, % Kalite, % Uzman

## 6. Veri Dağılımı
- Aylar arasında eşit olarak dağıtım
- Firma ve alt kırılımlara oranlara göre bölünme

## 7. Pivot Tablo & Grafikler
- Etki OSGB için ayrı pivot
- Etki Belgelendirme için ayrı pivot (alt kırılımlı)
- Grafikler: Firma bazlı dağılım ve zaman trendi

## 8. Geri Alma Butonu
- Son yükleme işlemini geri alır.

## 9. Otomatik Güncelleme Mantığı
- Aynı firma + aynı ay için yüklenen yeni dosya → eskisini siler, yenisiyle günceller.

## Kurulum
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
