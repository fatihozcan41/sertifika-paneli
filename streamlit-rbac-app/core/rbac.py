import streamlit as st
from .auth import get_current_user, user_has_permission
from .db import get_session

def require_permission(slug: str):
    def checker():
        with get_session() as db:
            user = get_current_user(db)
            if not user:
                st.error("Bu sayfa için giriş yapmalısınız.")
                st.stop()
            if not user_has_permission(user, slug, db):
                st.error(f"Bu alan için yetkiniz yok: {slug}")
                st.stop()
            return user, db
    return checker
