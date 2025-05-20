import asyncio
from aiogram import Bot, Dispatcher
from core.config import BOT_TOKEN
from bot.handlers import admin

# Главная асинхронная функция запуска бота
async def main():
    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)

    # Инициализация диспетчера Aiogram
    dp = Dispatcher()
    
    # Подключаем роутеры
    dp.include_router(admin.router)

    # Запускаем бесконечный polling
    await dp.start_polling(bot)

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
