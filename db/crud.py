from db.database import async_session
from db.models import User
from sqlalchemy import select, delete

# Функция для добавления нового пользователя в базу данных
async def add_user(telegram_id: str, username: str, phone: str, role: str):
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            phone=phone,
            role=role
        )
        session.add(user)
        await session.commit()

# Функция для удаления пользователя по username
async def delete_user(username: str):
    async with async_session() as session:
        stmt = delete(User).where(User.username == username)
        await session.execute(stmt)
        await session.commit()

# Функция для получения списка всех пользователей
async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
