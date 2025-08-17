from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from .base import Base

class Ratio(Base):
    __tablename__ = "ratios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    value = Column(Float, nullable=False)

class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(20), nullable=True)
    account = Column(String(120), nullable=True)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=True)
