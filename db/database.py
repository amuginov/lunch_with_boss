from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# URL подключения к SQLite (асинхронный драйвер aiosqlite)
DATABASE_URL = "sqlite+aiosqlite:///./users.db"

# Создание движка SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False)

# Сессия для выполнения запросов к базе
async_session = sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)
