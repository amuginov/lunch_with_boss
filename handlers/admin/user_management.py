from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["manage_users"]))
async def manage_users(message: Message):
    await message.answer("Здесь вы можете управлять пользователями.")