from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "/help")
async def cmd_help(message: Message):
    """
    Обработчик команды /help.
    Выводит справочную информацию по боту.
    """
    help_text = (
        "🍽 <b>Lunch Bot</b> — бот для бронирования обедов.\n\n"
        "Доступные команды:\n"
        "/start — начать работу с ботом\n"
        "/help — показать эту справку\n\n"
        "Если у вас есть вопросы, обратитесь к вашему администратору."
    )
    await message.answer(help_text)
