from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# Базовый класс для всех моделей
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = 'users'  # Название таблицы в БД

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID
    telegram_id = Column(String, unique=True)           # Telegram ID
    username = Column(String)                           # Telegram username
    phone = Column(String)                              # Телефон сотрудника
    role = Column(String)                               # Роль (admin / manager / employee)
