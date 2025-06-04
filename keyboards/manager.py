from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

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

def generate_date_keyboard() -> ReplyKeyboardMarkup:
    """
    Генерация клавиатуры с ближайшими 5 рабочими днями.
    """
    keyboard = []
    today = datetime.now()
    for i in range(5):
        day = today + timedelta(days=i)
        button_text = day.strftime("%A, %d %B")  # Пример: "Monday, 05 June"
        keyboard.append([KeyboardButton(text=button_text)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def generate_time_keyboard() -> ReplyKeyboardMarkup:
    """
    Генерация клавиатуры с часами (с 09:00 до 17:00).
    """
    keyboard = []
    for hour in range(9, 18):  # Часы с 09:00 до 17:00
        button_text = f"{hour:02d}:00"
        keyboard.append([KeyboardButton(text=button_text)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
