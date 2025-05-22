import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import common, help, admin, employee, manager

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем обработчики
    dp.include_router(common.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)
    dp.include_router(employee.router)
    dp.include_router(manager.router)

    # Устанавливаем команды для бота
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Помощь"),
    ])

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    