from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить пользователя")],
            [KeyboardButton(text="Настройки")],
            [KeyboardButton(text="Список пользователей")]  # Новая кнопка
        ],
        resize_keyboard=True
    )
