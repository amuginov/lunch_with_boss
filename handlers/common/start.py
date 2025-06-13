from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from db.crud import get_user_by_telegram_id
from keyboards.admin import admin_keyboard
from keyboards.manager import manager_keyboard
from keyboards.employee import employee_keyboard
from utils.common import return_to_main_menu

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)

    if user:
        if user.role == "admin":
            await return_to_main_menu(message, user.role, admin_keyboard())
        elif user.role == "manager":
            await return_to_main_menu(message, user.role, manager_keyboard())
        elif user.role == "user":
            await return_to_main_menu(message, user.role, employee_keyboard())
        else:
            await message.answer("Ваша роль не определена.")
    else:
        await message.answer("Вы не авторизованы. Обратитесь к администратору.")