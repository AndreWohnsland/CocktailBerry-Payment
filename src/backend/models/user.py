from sqlalchemy import Boolean, Column, Float, Integer, String

from src.backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nfc_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    is_adult = Column(Boolean, default=False, nullable=False)
