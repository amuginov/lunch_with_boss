from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from db.crud import get_user_by_telegram_id
from keyboards.common import main_menu_keyboard

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Проверяет, есть ли пользователь в базе,
    приветствует и предлагает главное меню.
    """
    user = await get_user_by_telegram_id(str(message.from_user.id))

    if user:
        # Пользователь зарегистрирован, приветствуем и показываем главное меню
        await message.answer(
            f"Привет, {user.username}! Добро пожаловать в Lunch Bot.",
            reply_markup=main_menu_keyboard(user.role)
        )
    else:
        # Пользователь не найден — предлагаем связаться с администратором
        await message.answer(
            "Здравствуйте! Вы не зарегистрированы в системе.\n"
            "Пожалуйста, обратитесь к администратору для доступа."
        )
