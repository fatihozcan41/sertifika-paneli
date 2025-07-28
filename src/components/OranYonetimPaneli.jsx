import React, { useState } from "react";

const initialOran = {
  osgb: "",
  belge: "",
  egitim: "",
  ilkyardim: "",
  kalite: "",
  uzmanlik: ""
};

export default function OranYonetimPaneli({ yeniHesapIsmi, onOranKaydet }) {
  const [hesapIsmi, setHesapIsmi] = useState(yeniHesapIsmi || "");
  const [oranlar, setOranlar] = useState(initialOran);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setOranlar({ ...oranlar, [name]: value });
  };

  const handleAddOran = () => {
    if (!hesapIsmi) return alert("HESAP İSMİ giriniz.");
    const toplamBelgeAlt =
      Number(oranlar.egitim) +
      Number(oranlar.ilkyardim) +
      Number(oranlar.kalite) +
      Number(oranlar.uzmanlik);

    if (toplamBelgeAlt !== 100) {
      return alert("Belgelendirme alt dağılımı toplamı %100 olmalıdır.");
    }
    if (Number(oranlar.osgb) + Number(oranlar.belge) !== 100) {
      return alert("Etki OSGB ve Etki Belgelendirme oranları toplamı %100 olmalıdır.");
    }

    const yeniOran = { hesapIsmi, ...oranlar };
    onOranKaydet(yeniOran);
    alert("Oran başarıyla kaydedildi.");
  };

  return (
    <div className="p-4 border rounded-xl shadow-lg">
      <h2 className="text-xl font-bold mb-4">Oran Tanımlama</h2>
      <input
        type="text"
        placeholder="HESAP İSMİ"
        className="p-2 border w-full mb-2"
        value={hesapIsmi}
        onChange={(e) => setHesapIsmi(e.target.value)}
        disabled={!!yeniHesapIsmi}
      />

      <div className="grid grid-cols-2 gap-4">
        <input type="number" name="osgb" placeholder="Etki OSGB (%)" className="p-2 border" value={oranlar.osgb} onChange={handleChange} />
        <input type="number" name="belge" placeholder="Etki Belgelendirme (%)" className="p-2 border" value={oranlar.belge} onChange={handleChange} />
        <input type="number" name="egitim" placeholder="EĞİTİM (%)" className="p-2 border" value={oranlar.egitim} onChange={handleChange} />
        <input type="number" name="ilkyardim" placeholder="İLKYARDIM (%)" className="p-2 border" value={oranlar.ilkyardim} onChange={handleChange} />
        <input type="number" name="kalite" placeholder="KALİTE DANIŞMANLIK (%)" className="p-2 border" value={oranlar.kalite} onChange={handleChange} />
        <input type="number" name="uzmanlik" placeholder="UZMANLIK (%)" className="p-2 border" value={oranlar.uzmanlik} onChange={handleChange} />
      </div>

      <button
        className="mt-4 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        onClick={handleAddOran}
      >
        Oranı Kaydet
      </button>
    </div>
  );
}
