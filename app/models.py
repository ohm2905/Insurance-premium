from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    predictions = relationship("InsuranceRecord", back_populates="user")


class InsuranceRecord(Base):
    __tablename__ = "insurance_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    bmi = Column(Float, nullable=False)
    children = Column(Integer, nullable=False)
    smoker = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False)
    predicted_premium = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    user_id = Column(String, ForeignKey("users.id"))

    user = relationship("User", back_populates="predictions")
