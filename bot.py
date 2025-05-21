from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
import asyncio

from config import BOT_TOKEN  # Импорт токена из конфигурации
from handlers.admin import user_management  # Импорт модуля администратора
from handlers.common import start, help  # Импорт общих хэндлеров
from handlers.manager import schedule  # Импорт менеджерских хэндлеров
from handlers.employee import booking  # Импорт хэндлеров сотрудников

async def main():
    """
    Основная асинхронная функция запуска бота.
    Создаёт объекты бота и диспетчера,
    регистрирует хэндлеры, задаёт команды,
    запускает поллинг.
    """

    # Инициализация бота с токеном
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

    # Хранилище состояний в памяти (для FSM)
    storage = MemoryStorage()

    # Диспетчер — центральный объект для регистрации и обработки событий
    dp = Dispatcher(storage=storage)

    # Регистрируем маршруты (хэндлеры) из разных модулей
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(user_management.router)
    dp.include_router(schedule.router)
    dp.include_router(booking.router)

    # Устанавливаем список команд, которые пользователи увидят в Telegram меню
    await bot.set_my_commands([
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Помощь по боту"),
        # Можно добавить другие команды для разных ролей
    ])

    print("Бот запущен...")

    # Запускаем долгоживущее получение обновлений от Telegram (поллинг)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запуск асинхронной main() через asyncio
    asyncio.run(main())
