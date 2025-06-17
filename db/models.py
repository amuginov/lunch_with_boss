from sqlalchemy import Column, Integer, String, BigInteger, Boolean, TIMESTAMP, Time, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)  # Telegram ID
    last_name = Column(String, nullable=False)  # Фамилия
    first_name = Column(String, nullable=False)  # Имя
    middle_name = Column(String, nullable=True)  # Отчество
    phone_number = Column(String, nullable=False)
    role = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)  # Email

    # Связь с LunchSlot через manager_id
    lunch_slots = relationship("LunchSlot", back_populates="manager", foreign_keys="[LunchSlot.manager_id]")

    # Связь с LunchSlot через booked_by_user_id
    booked_slots = relationship("LunchSlot", back_populates="booked_by_user", foreign_keys="[LunchSlot.booked_by_user_id]")

class LunchSlot(Base):
    __tablename__ = "lunch_slots"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)  # Время окончания формируется автоматически
    capacity = Column(Integer, default=1, nullable=False)  # Количество мест всегда 1
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Привязка к менеджеру
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    manager = relationship("User", back_populates="lunch_slots", foreign_keys=[manager_id])

    # Поле для проверки, забронирован ли слот
    is_booked = Column(Boolean, default=False)

    # Поле для хранения ID пользователя, который забронировал слот
    booked_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    booked_by_user = relationship("User", back_populates="booked_slots", foreign_keys=[booked_by_user_id])

    # Новое поле для хранения ID события Google Calendar
    event_id = Column(String, nullable=True)