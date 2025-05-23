from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer("Вот список доступных команд:\n/start - Начать\n/help - Помощь")