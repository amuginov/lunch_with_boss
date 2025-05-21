from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from db.models import Base

# Указываем SQLite БД, можно заменить на PostgreSQL или другую при необходимости
DATABASE_URL = "sqlite+aiosqlite:///./lunch_bot.db"

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика асинхронных сессий
async_session = async_sessionmaker(engine, expire_on_commit=False)

# Функция для создания всех таблиц (вызывается при старте)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
