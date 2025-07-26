
from pathlib import Path
import pandas as pd

# Arşiv klasörü tanımı
arsiv_klasoru = Path("arsiv")
arsiv_klasoru.mkdir(exist_ok=True)

# Dosya listesini al
dosya_listesi = list(arsiv_klasoru.glob("*.csv"))

# Örnek çıktı
for dosya in dosya_listesi:
    print("Bulunan dosya:", dosya.name)
