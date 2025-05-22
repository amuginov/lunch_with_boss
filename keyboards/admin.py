from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Управление пользователями")],
            [KeyboardButton(text="Настройки")]
        ],
        resize_keyboard=True
    )
