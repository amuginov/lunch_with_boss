from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["schedule"]))
async def schedule_command(message: Message):
    await message.answer("Здесь вы можете управлять расписанием.")