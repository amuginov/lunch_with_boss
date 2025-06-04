from sqlalchemy import Column, Integer, String, BigInteger, Boolean, TIMESTAMP, Time, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(15), nullable=True)
    role = Column(String(50), default="unauth_user")  # admin, user, manager, unauth_user
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class LunchSlot(Base):
    __tablename__ = "lunch_slots"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)  # Время окончания формируется автоматически
    capacity = Column(Integer, default=1, nullable=False)  # Количество мест всегда 1
    created_at = Column(TIMESTAMP, default=datetime.utcnow)