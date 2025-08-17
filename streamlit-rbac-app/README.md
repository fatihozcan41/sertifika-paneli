# Streamlit RBAC Uygulaması

Rol tabanlı yetkilendirme (RBAC) ve kimlik doğrulama içeren, Streamlit tabanlı kontrol paneli iskeleti.
- Kullanıcı girişi (kullanıcı adı/e‑posta + parola)
- Roller: `admin`, `editor`, `viewer`
- İzinler: `users.read|create|edit|delete`, `data.upload`, `ratios.manage`, `reports.read`
- Kullanıcı CRUD (admin/editor), rol atama
- SQLite varsayılan, PostgreSQL opsiyonel
- Streamlit Community Cloud'a uygun, GitHub deposu olarak çalışır

## Kurulum (Yerel)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
python -m core.seed
streamlit run app.py
```

## Ortam Ayarları
`secrets.toml` içinde ilk admin bilgileri bulunur. İlk girişten sonra parolayı değiştirmeniz önerilir.
- `DATABASE_URL` boşsa SQLite kullanılır: `sqlite:///app.db`

## Deploy (Streamlit Cloud)
- Depoyu GitHub'a yükleyin.
- New app → `app.py` ana dosya.
- **Secrets** bölümüne `.streamlit/secrets.toml.example` içeriğini ekleyin.
- Deploy.

## Not
Bu iskelet, Bootstrap görünümüne yakın his için statik CSS içerir; isterseniz resmi Bootstrap dosyasını `static/` içine ekleyip sayfada kullanabilirsiniz.
