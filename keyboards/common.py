from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    """
    Клавиатура с основными командами.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start"), KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )

def registration_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Регистрация")],  # Изменено название кнопки
            [KeyboardButton(text="Помощь")]
        ],
        resize_keyboard=True
    )
