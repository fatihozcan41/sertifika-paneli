from sqlalchemy import select
from sqlalchemy.orm import Session
from models.base import Base
from models.user import User
from models.role import Role
from models.permission import Permission
from models.role_user import RoleUser
from models.permission_role import PermissionRole
from core.db import init_engine
from core.security import hash_password
import streamlit as st

PERMISSIONS = [
    ("Kullanıcıları Görüntüle", "users.read"),
    ("Kullanıcı Oluştur", "users.create"),
    ("Kullanıcı Düzenle", "users.edit"),
    ("Kullanıcı Sil", "users.delete"),
    ("Veri Yükle", "data.upload"),
    ("Oranları Yönet", "ratios.manage"),
    ("Raporları Gör", "reports.read"),
]

ROLES = [
    ("Yönetici", "admin"),
    ("Editör", "editor"),
    ("Görüntüleyici", "viewer"),
]

def main():
    engine, SessionLocal = init_engine()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        # create roles
        for name, slug in ROLES:
            if not db.execute(select(Role).where(Role.slug==slug)).scalar_one_or_none():
                db.add(Role(name=name, slug=slug))
        db.commit()

        # create permissions
        for name, slug in PERMISSIONS:
            if not db.execute(select(Permission).where(Permission.slug==slug)).scalar_one_or_none():
                db.add(Permission(name=name, slug=slug))
        db.commit()

        # attach permissions to roles
        admin = db.execute(select(Role).where(Role.slug=="admin")).scalar_one()
        viewer = db.execute(select(Role).where(Role.slug=="viewer")).scalar_one()

        for perm in db.execute(select(Permission)).scalars():
            # grant all to admin
            if not db.execute(select(PermissionRole).where(PermissionRole.role_id==admin.id, PermissionRole.permission_id==perm.id)).scalar_one_or_none():
                db.add(PermissionRole(role_id=admin.id, permission_id=perm.id))
            # viewer only read permissions
            if perm.slug in ("users.read", "reports.read"):
                if not db.execute(select(PermissionRole).where(PermissionRole.role_id==viewer.id, PermissionRole.permission_id==perm.id)).scalar_one_or_none():
                    db.add(PermissionRole(role_id=viewer.id, permission_id=perm.id))
        db.commit()

        # create admin user
        admin_name = st.secrets.get("ADMIN_NAME", "Sistem Yöneticisi")
        admin_email = st.secrets.get("ADMIN_EMAIL", "admin@example.com")
        admin_username = st.secrets.get("ADMIN_USERNAME", "admin")
        admin_password = st.secrets.get("ADMIN_PASSWORD", "ChangeMe_123!")

        if not db.execute(select(User).where(User.email==admin_email)).scalar_one_or_none():
            u = User(
                name=admin_name,
                email=admin_email,
                username=admin_username,
                password_hash=hash_password(admin_password),
                status=True,
            )
            db.add(u)
            db.commit()
            db.refresh(u)
            db.add(RoleUser(user_id=u.id, role_id=admin.id))
            db.commit()
            print("Admin kullanıcı oluşturuldu:", admin_email)
        else:
            print("Admin kullanıcı mevcut:", admin_email)

if __name__ == "__main__":
    main()
