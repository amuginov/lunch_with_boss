from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from db.crud import get_user_by_telegram_id
from keyboards.admin import admin_keyboard

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    # Получаем пользователя из базы данных
    user = get_user_by_telegram_id(message.from_user.id)

    if user:
        if user.role == "admin":
            # Отправляем клавиатуру администратора
            await message.answer("Добро пожаловать, администратор!", reply_markup=admin_keyboard())
        else:
            # Отправляем сообщение для обычного пользователя
            await message.answer("Добро пожаловать! Вы пользователь.")
    else:
        # Если пользователь не найден, регистрируем его как неавторизованного
        await message.answer("Вы не авторизованы. Обратитесь к администратору.")