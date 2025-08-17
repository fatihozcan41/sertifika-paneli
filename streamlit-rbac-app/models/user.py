from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(191), unique=True, nullable=False)
    username = Column(String(60), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    force_password_change = Column(Boolean, default=False, nullable=False)

    roles = relationship("Role", secondary="role_user", back_populates="users")
