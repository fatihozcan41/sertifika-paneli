
import streamlit as st
import sqlite3
import os
from datetime import datetime

st.set_page_config(page_title="Gelişmiş Sertifika Paneli", layout="centered")

# Kullanıcı kontrolü
def check_login(username, password):
    users = {"admin": "1234", "fatih": "12345"}
    return users.get(username) == password

# Veritabanı bağlantısı ve gelişmiş tablo
def get_db():
    conn = sqlite3.connect("sertifikalar.db", check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS sertifikalar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sertifika_no TEXT,
        sertifika_kodu TEXT,
        ogrenci_ad_soyad TEXT,
        tc_no TEXT,
        dogum_tarihi TEXT,
        eposta TEXT,
        telefon TEXT,
        kurum TEXT,
        unvan TEXT,
        egitim_adi TEXT,
        egitim_kodu TEXT,
        egitim_suresi INTEGER,
        egitim_yeri TEXT,
        egitim_baslangic TEXT,
        egitim_bitis TEXT,
        egitmen_adi TEXT,
        sertifika_tarihi TEXT,
        gecerlilik_tarihi TEXT,
        sertifika_turu TEXT,
        sertifika_durumu TEXT,
        sertifika_dili TEXT,
        teslim_durumu TEXT,
        yenileme_gerekli TEXT,
        yenileme_tarihi TEXT,
        gorsel_path TEXT
    )""")
    return conn

st.title("🎓 Gelişmiş Sertifika Yönetimi")

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
st.success("Veritabanı yapısı hazır. Gelişmiş panel buradan devam ettirilebilir.")
