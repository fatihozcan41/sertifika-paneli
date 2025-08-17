from sqlalchemy import Column, Integer, ForeignKey, Table, UniqueConstraint
from .base import Base
from sqlalchemy.orm import declarative_mixin

class RoleUser(Base):
    __tablename__ = "role_user"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
