import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_url():
    # Prefer secrets, fallback to SQLite
    db_url = st.secrets.get("DATABASE_URL", "")
    if not db_url:
        # local sqlite
        return "sqlite:///app.db"
    return db_url

_engine = None
_SessionLocal = None

def init_engine():
    global _engine, _SessionLocal
    if _engine is None:
        url = get_db_url()
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(url, echo=False, future=True, connect_args=connect_args)
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine, _SessionLocal

def get_session():
    if _SessionLocal is None:
        init_engine()
    return _SessionLocal()
