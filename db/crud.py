from db.database import async_session
from db.models import User
from sqlalchemy.future import select

# Добавление нового пользователя в БД
async def add_user(telegram_id, username, phone, role):
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            phone=phone,
            role=role
        )
        session.add(user)
        await session.commit()

# Получение всех пользователей
async def get_all_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()
