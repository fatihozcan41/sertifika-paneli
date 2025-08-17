from sqlalchemy import Column, Integer, ForeignKey
from .base import Base

class PermissionRole(Base):
    __tablename__ = "permission_role"
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
