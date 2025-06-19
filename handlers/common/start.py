from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F
from db.crud import get_user_by_telegram_id
from keyboards.admin import admin_keyboard
from keyboards.manager import manager_keyboard
from keyboards.employee import employee_keyboard
from keyboards.common import registration_keyboard
from utils.common import return_to_main_menu
from db.database import SessionLocal

router = Router()

@router.message(F.text == "/start")
async def start_command(message: Message):
    telegram_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    with SessionLocal() as session:
        user = get_user_by_telegram_id(session, telegram_id)

    if user:
        # Отправляем клавиатуру в зависимости от роли пользователя
        if user.role == "admin":
            await message.answer(
                "Добро пожаловать, администратор!",
                reply_markup=admin_keyboard()
            )
        elif user.role == "manager":
            await message.answer(
                "Добро пожаловать, менеджер!",
                reply_markup=manager_keyboard()
            )
        elif user.role == "user":
            await message.answer(
                "Добро пожаловать, пользователь!",
                reply_markup=employee_keyboard()
            )
    else:
        # Если пользователь не зарегистрирован, отправляем клавиатуру для подачи заявки
        await message.answer(
            "Добро пожаловать! Вы не зарегистрированы. Пожалуйста, подайте заявку на регистрацию.",
            reply_markup=registration_keyboard()
        )

@router.message(Command(commands=["myid"]))
async def my_id_command(message: Message):
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")