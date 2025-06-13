from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import locale
from utils.common import WEEKDAY_SHORTCUTS, MONTH_SHORTCUTS

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

def generate_time_inline_keyboard():
    """
    Генерация клавиатуры с часами (с 09:00 до 17:00) в виде Inline-кнопок (3 ряда, 3 строки).
    """
    keyboard = []  # Список для строк кнопок
    row = []  # Текущая строка кнопок
    for hour in range(9, 18):  # Часы с 09:00 до 17:00
        button_text = f"{hour:02d}:00"
        callback_data = f"select_time:{hour:02d}:00"  # Формируем callback_data
        row.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))
        
        if len(row) == 3:  # Если в строке 3 кнопки, добавляем её в клавиатуру
            keyboard.append(row)
            row = []  # Очищаем строку для следующей группы кнопок
    
    if row:  # Добавляем оставшиеся кнопки, если они есть
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def generate_slots_keyboard(slots):
    """
    Генерация клавиатуры для списка слотов.
    :param slots: Список объектов LunchSlot.
    :return: InlineKeyboardMarkup.
    """
    inline_keyboard = []
    for slot in slots:
        # Сокращаем день недели и месяц
        weekday = WEEKDAY_SHORTCUTS[slot.date.strftime("%A")]
        month = MONTH_SHORTCUTS[slot.date.strftime("%m")]
        formatted_date = f"{weekday}, {slot.date.day} {month}"
        formatted_time = slot.start_time.strftime("%H:%M")
        button_text = f"{formatted_date}, {formatted_time}"

        # Кнопка для деталей слота
        detail_button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"slot_detail:{slot.id}"
        )
        # Кнопка для удаления слота
        delete_button = InlineKeyboardButton(
            text="❌",  # Используем символ вместо текста для минимального размера
            callback_data=f"delete_slot:{slot.id}"
        )
        inline_keyboard.append([detail_button, delete_button])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)