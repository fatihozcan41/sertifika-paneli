from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    slug = Column(String(80), unique=True, nullable=False)

    roles = relationship("Role", secondary="permission_role", back_populates="permissions")
