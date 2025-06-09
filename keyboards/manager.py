from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import locale

# Устанавливаем локаль на русский
locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

def manager_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для роли manager
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Новый слот"), KeyboardButton(text="📋 Мои слоты")],  # Первый ряд
            [KeyboardButton(text="❓ Помощь")],  # Второй ряд
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
    added_days = 0  # Счетчик добавленных рабочих дней

    while added_days < 5:  # Добавляем только 5 рабочих дней
        day = today + timedelta(days=added_days)
        weekday = day.weekday()  # 0 = Понедельник, 6 = Воскресенье

        if weekday < 5:  # Если день не суббота (5) и не воскресенье (6)
            button_text = day.strftime("%A, %d %B")  # Пример: "Понедельник, 05 июня"
            keyboard.append([KeyboardButton(text=button_text.capitalize())])  # Делаем первую букву заглавной
        else:
            # Если день суббота или воскресенье, пропускаем его
            today += timedelta(days=1)
            continue

        added_days += 1

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def generate_time_keyboard() -> ReplyKeyboardMarkup:
    """
    Генерация клавиатуры с часами (с 09:00 до 17:00) в 3 столбца.
    """
    keyboard = []
    row = []
    for hour in range(9, 18):  # Часы с 09:00 до 17:00
        button_text = f"{hour:02d}:00"
        row.append(KeyboardButton(text=button_text))
        if len(row) == 3:  # Если в строке 3 кнопки, добавляем её в клавиатуру
            keyboard.append(row)
            row = []
    if row:  # Добавляем оставшиеся кнопки, если они есть
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)