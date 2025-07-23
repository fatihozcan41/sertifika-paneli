
import streamlit as st
import sqlite3
import os
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Sertifika Paneli", layout="centered")

def check_login(username, password):
    users = {"admin": "1234", "fatih": "12345"}
    return users.get(username) == password

def get_db():
    conn = sqlite3.connect("sertifikalar.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS sertifikalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sertifika_no TEXT,
        ogrenci_ad_soyad TEXT,
        egitim_adi TEXT,
        telefon TEXT,
        sertifika_tarihi TEXT,
        gorsel_path TEXT
    )""")
    return conn

def list_sertifikalar(search=""):
    cursor = conn.cursor()
    if search:
        cursor.execute("SELECT * FROM sertifikalar WHERE ogrenci_ad_soyad LIKE ?", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM sertifikalar")
    return cursor.fetchall()

st.title("🎓 Sertifika Takip Paneli")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        st.subheader("🔐 Giriş Yap")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş")
        if submitted and check_login(username, password):
            st.session_state.logged_in = True
            st.success("Giriş başarılı.")
        elif submitted:
            st.error("Kullanıcı adı veya şifre hatalı.")
    st.stop()

conn = get_db()

st.subheader("➕ Yeni Sertifika Ekle")
with st.form("add_cert"):
    col1, col2 = st.columns(2)
    with col1:
        sertifika_no = st.text_input("Sertifika No")
        ogrenci_ad_soyad = st.text_input("Öğrenci Adı Soyadı")
        telefon = st.text_input("Telefon")
        sertifika_tarihi = st.date_input("Sertifika Tarihi", value=datetime.today())
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
        conn.execute("INSERT INTO sertifikalar (sertifika_no, ogrenci_ad_soyad, egitim_adi, telefon, sertifika_tarihi, gorsel_path) VALUES (?, ?, ?, ?, ?, ?)",
                     (sertifika_no, ogrenci_ad_soyad, egitim_adi, telefon, sertifika_tarihi.strftime("%Y-%m-%d"), gorsel_path))
        conn.commit()
        st.success("Sertifika kaydedildi.")

st.subheader("📋 Sertifika Listesi")
search_term = st.text_input("🔍 Öğrenci Adı ile Ara")
data = list_sertifikalar(search_term)

if data:
    for row in data:
        with st.expander(f"{row[2]} ({row[1]})"):
            st.write(f"**Eğitim Adı:** {row[3]}")
            st.write(f"**Telefon:** {row[4]}")
            st.write(f"**Sertifika Tarihi:** {row[5]}")
            if row[6] and os.path.exists(row[6]):
                if row[6].endswith(".pdf"):
                    st.write(f"[📄 PDF Görüntüle]({row[6]})")
                else:
                    st.image(row[6], width=300)
else:
    st.info("Kayıt bulunamadı.")
