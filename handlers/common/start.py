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
    user = get_user_by_telegram_id(telegram_id)  # Передаём только telegram_id

    if user:
        # Отправляем приветствие в зависимости от роли пользователя
        if user.role == "admin":
            await message.answer(
                "🛠 Администратор\n"
                "Добро пожаловать в панель администратора!\n\n"
                "👥 Управляйте пользователями: добавляйте и удаляйте сотрудников и руководителей.\n"
                "📨 Обрабатывайте заявки на регистрацию — одобряйте или отклоняйте по своему усмотрению.",
                reply_markup=admin_keyboard()
            )
        elif user.role == "manager":
            await message.answer(
                "Добро пожаловать!\n\n"
                "📅 По кнопке «Забронировать слот» Вы можете управлять своим обеденным расписанием — добавлять свободное время, когда готовы встретиться с коллегами.\n"
                "🔍 В разделе «Мои слоты» Вы сможете просматривать и при необходимости удалять ранее добавленные слоты.\n"
                "📧 Забронированные слоты для обеда будут автоматически отправляться в Ваш календарь по электронной почте.",
                reply_markup=manager_keyboard()
            )
        elif user.role == "user":
            await message.answer(
                "Рады вас видеть!\n\n"
                "🍽 Нажмите «Забронировать обед», чтобы выбрать удобное время для встречи с руководителем.\n"
                "📋 В разделе «Мои бронирования» Вы можете просматривать и управлять своими обедами.\n"
                "📧 Подтверждения придут в Ваш календарь по электронной почте.",
                reply_markup=employee_keyboard()
            )
    else:
        # Приветствие для неавторизованного пользователя
        await message.answer(
            "🚫 Неавторизованный пользователь\n"
            "Здравствуйте!\n\n"
            "Этот бот помогает планировать совместные обеды между руководителями и сотрудниками.\n"
            "🔐 Чтобы начать — пройдите простую регистрацию, нажав кнопку «Регистрация».",
            reply_markup=registration_keyboard()
        )

@router.message(Command(commands=["myid"]))
async def my_id_command(message: Message):
    await message.answer(f"Ваш Telegram ID: {message.from_user.id}")