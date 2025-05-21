from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Модель таблицы пользователей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)       # Внутренний ID пользователя
    telegram_id = Column(String, unique=True)                # Telegram ID (уникален)
    username = Column(String)                                # Username пользователя в Telegram
    phone = Column(String)                                   # Телефон
    role = Column(String)                                    # Роль: admin / manager / employee
