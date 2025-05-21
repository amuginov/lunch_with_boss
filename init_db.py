import asyncio
from db.models import Base
from db.database import engine

# Создание всех таблиц в базе данных
async def create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Запуск скрипта
asyncio.run(create())
