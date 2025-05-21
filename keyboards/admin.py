from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для роли admin
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить пользователя")],
            [KeyboardButton(text="➖ Удалить пользователя")],
            [KeyboardButton(text="📋 Список пользователей")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )
