from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from db.crud import get_user_by_telegram_id
from keyboards.admin import admin_keyboard
from keyboards.manager import manager_keyboard  # Импортируем клавиатуру для менеджера
from keyboards.employee import employee_keyboard  # Импортируем клавиатуру для пользователя

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    # Получаем пользователя из базы данных
    user = get_user_by_telegram_id(message.from_user.id)

    if user:
        if user.role == "admin":
            # Отправляем клавиатуру администратора
            await message.answer("Добро пожаловать, администратор!", reply_markup=admin_keyboard())
        elif user.role == "manager":
            # Отправляем клавиатуру менеджера
            await message.answer("Добро пожаловать, менеджер!", reply_markup=manager_keyboard())
        elif user.role == "user":
            # Отправляем клавиатуру пользователя
            await message.answer("Добро пожаловать! Вы пользователь.", reply_markup=employee_keyboard())
        else:
            # Если роль неизвестна, отправляем сообщение без клавиатуры
            await message.answer("Добро пожаловать! Ваша роль не определена.")
    else:
        # Если пользователь не найден, регистрируем его как неавторизованного
        await message.answer("Вы не авторизованы. Обратитесь к администратору.")