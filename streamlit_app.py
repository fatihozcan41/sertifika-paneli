
import streamlit as st
import sqlite3
import os
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Sertifika Paneli", layout="centered")

# --- Kullanıcı doğrulama ---
def check_login(username, password):
    users = {
        "admin": "1234",
        "fatih": "12345"
    }
    return users.get(username) == password

# --- Veritabanı bağlantısı ---
def get_db():
    conn = sqlite3.connect("sertifikalar.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS sertifikalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sertifika_no TEXT,
        ogrenci_ad_soyad TEXT,
        egitim_adi TEXT,
        telefon TEXT,
        gorsel_path TEXT
    )""")
    return conn

# --- Sertifika listeleme ---
def list_sertifikalar(search=""):
    cursor = conn.cursor()
    if search:
        cursor.execute("SELECT * FROM sertifikalar WHERE ogrenci_ad_soyad LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM sertifikalar")
    return cursor.fetchall()

# --- Başlık ---
st.title("🎓 Sertifika Takip Paneli")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Giriş Ekranı ---
if not st.session_state.logged_in:
    with st.form("login"):
        st.subheader("🔐 Giriş Yap")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş")

        if submitted:
            if check_login(username, password):
                st.session_state.logged_in = True
                st.success("Giriş başarılı.")
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")
    st.stop()

# --- Veritabanını başlat ---
conn = get_db()

# --- Sertifika Ekleme ---
st.subheader("➕ Yeni Sertifika Ekle")
with st.form("add_cert"):
    col1, col2 = st.columns(2)
    with col1:
        sertifika_no = st.text_input("Sertifika No")
        ogrenci_ad_soyad = st.text_input("Öğrenci Adı Soyadı")
        telefon = st.text_input("Telefon")
    with col2:
        egitim_adi = st.text_input("Eğitim Adı")
        gorsel = st.file_uploader("Sertifika Görseli", type=["jpg", "jpeg", "png", "pdf"])

    ekle = st.form_submit_button("Kaydet")
    if ekle:
        gorsel_path = ""
        if gorsel:
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            gorsel_path = os.path.join(upload_dir, f"{datetime.now().timestamp()}_{gorsel.name}")
            with open(gorsel_path, "wb") as f:
                f.write(gorsel.getbuffer())

        conn.execute("INSERT INTO sertifikalar (sertifika_no, ogrenci_ad_soyad, egitim_adi, telefon, gorsel_path) VALUES (?, ?, ?, ?, ?)",
                     (sertifika_no, ogrenci_ad_soyad, egitim_adi, telefon, gorsel_path))
        conn.commit()
        st.success("Sertifika kaydedildi.")

# --- Sertifika Listesi ---
st.subheader("📋 Sertifika Listesi")

search_term = st.text_input("🔍 Öğrenci Adı ile Ara")
data = list_sertifikalar(search_term)

if data:
    for row in data:
        with st.expander(f"{row[2]} ({row[1]})"):
            st.write(f"**Eğitim Adı:** {row[3]}")
            st.write(f"**Telefon:** {row[4]}")
            if row[5] and os.path.exists(row[5]):
                if row[5].endswith(".pdf"):
                    st.write(f"[📄 PDF Görüntüle]({row[5]})")
                else:
                    st.image(row[5], width=300)
else:
    st.info("Kayıt bulunamadı.")
