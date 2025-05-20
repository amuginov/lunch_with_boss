from fastapi import APIRouter
from db.crud import get_all_users

# Роутер FastAPI для работы с пользователями
router = APIRouter()

# GET-запрос на получение всех пользователей
@router.get("/users")
async def list_users():
    users = await get_all_users()
    # Преобразуем объекты User в словари
    return [dict(
        id=u.id,
        username=u.username,
        phone=u.phone,
        role=u.role
    ) for u in users]
