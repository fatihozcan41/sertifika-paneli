import React from "react";
import OranYonetimPaneli from "./OranYonetimPaneli";

export default function OranKontrolPopup({ hesapIsmi, onKaydet }) {
  return (
    <div className="fixed top-0 left-0 w-full h-full bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-xl w-full max-w-2xl shadow-2xl">
        <p className="mb-4 text-red-600 font-semibold">
          "{hesapIsmi}" için tanımlı oran bulunamadı. Lütfen oranları giriniz.
        </p>
        <OranYonetimPaneli yeniHesapIsmi={hesapIsmi} onOranKaydet={onKaydet} />
      </div>
    </div>
  );
}
