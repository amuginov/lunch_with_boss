from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def employee_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для роли employee
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍽 Забронировать обед")],
            [KeyboardButton(text="📋 Мои бронирования")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )
