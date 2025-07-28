import React, { useState } from "react";
import OranKontrolPopup from "./OranKontrolPopup";

const tanimliOranlar = [];

export default function VeriGirisiFormu() {
  const [formData, setFormData] = useState({
    firma: "",
    tur: "",
    ay: "",
    tarih: "",
    hesapIsmi: "",
    tutar: "",
    sorumluluk: ""
  });
  const [gosterPopup, setGosterPopup] = useState(false);
  const [oranEksiHesap, setOranEksiHesap] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const oranVarMi = (hesap) => {
    return tanimliOranlar.some((oran) => oran.hesapIsmi === hesap);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const kontrolEt = ["BELGE ORTAK GİDER", "OSGB + BELGE ORTAK GİDER"].includes(
      formData.sorumluluk.toUpperCase()
    );
    const oranVar = oranVarMi(formData.hesapIsmi);

    if (kontrolEt && !oranVar) {
      setOranEksiHesap(formData.hesapIsmi);
      setGosterPopup(true);
      return;
    }

    console.log("Veri Gönderildi:", formData);
    alert("Veri kaydedildi (örnek)");
  };

  const oranKaydet = (oran) => {
    tanimliOranlar.push(oran);
    setGosterPopup(false);
    alert("Oran tanımı alındı. Lütfen işlemi tekrar gönderin.");
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="p-4 border rounded-xl shadow-lg">
        <h2 className="text-xl font-bold mb-4">Veri Girişi</h2>

        <div className="grid grid-cols-2 gap-4">
          <select name="firma" className="p-2 border" onChange={handleChange} required>
            <option value="">Firma Seçiniz</option>
            <option value="Etki OSGB">Etki OSGB</option>
            <option value="Etki Belgelendirme">Etki Belgelendirme</option>
          </select>

          <select name="tur" className="p-2 border" onChange={handleChange} required>
            <option value="">İşlem Türü</option>
            <option value="Gelir">Gelir</option>
            <option value="Gider">Gider</option>
          </select>

          <select name="ay" className="p-2 border" onChange={handleChange} required>
            <option value="">Ay Seçiniz</option>
            {["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"].map((ay) => (
              <option key={ay} value={ay}>{ay}</option>
            ))}
          </select>

          <input
            type="date"
            name="tarih"
            className="p-2 border"
            value={formData.tarih}
            onChange={handleChange}
          />

          <input
            type="text"
            name="hesapIsmi"
            placeholder="Hesap İsmi"
            className="p-2 border"
            value={formData.hesapIsmi}
            onChange={handleChange}
          />

          <input
            type="number"
            name="tutar"
            placeholder="Tutar"
            className="p-2 border"
            value={formData.tutar}
            onChange={handleChange}
          />

          <input
            type="text"
            name="sorumluluk"
            placeholder="Sorumluluk Merkezi"
            className="p-2 border"
            value={formData.sorumluluk}
            onChange={handleChange}
          />
        </div>

        <button
          type="submit"
          className="mt-4 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
        >
          Kaydet
        </button>
      </form>

      {gosterPopup && (
        <OranKontrolPopup hesapIsmi={oranEksiHesap} onKaydet={oranKaydet} />
      )}
    </>
  );
}
