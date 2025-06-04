from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить пользователя")],
            [KeyboardButton(text="Список пользователей")],
            [KeyboardButton(text="Удалить пользователя")],  # Новая кнопка
            [KeyboardButton(text="Настройки")]
        ],
        resize_keyboard=True
    )
