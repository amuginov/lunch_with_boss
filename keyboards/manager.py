from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def manager_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для роли manager
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Управление слотами обедов")],
            [KeyboardButton(text="📋 Список пользователей")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )
