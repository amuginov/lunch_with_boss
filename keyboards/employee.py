from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.common import WEEKDAY_SHORTCUTS, MONTH_SHORTCUTS

def employee_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура для роли employee
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍽 Забронировать обед")],
            [KeyboardButton(text="📋 Мои бронирования")],
            [KeyboardButton(text="Помощь")],  # Добавляем кнопку "Помощь"
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )

def generate_booking_keyboard(bookings):
    """
    Генерация клавиатуры для списка бронирований.
    :param bookings: Список словарей с данными о бронированиях.
    :return: InlineKeyboardMarkup.
    """
    inline_keyboard = []
    for booking in bookings:
        # Форматируем дату и время
        weekday = WEEKDAY_SHORTCUTS[booking["date"].strftime("%A")]
        month = MONTH_SHORTCUTS[booking["date"].strftime("%m")]
        formatted_date = f"{weekday}, {booking['date'].day} {month}"
        formatted_time = booking["start_time"].strftime("%H:%M")
        button_text = f"{formatted_date}, {formatted_time}, {booking['manager_name']}"

        # Кнопка для деталей бронирования
        detail_button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"detail_booking:{booking['id']}"
        )
        # Кнопка для удаления бронирования
        delete_button = InlineKeyboardButton(
            text="❌",
            callback_data=f"delete_booking:{booking['id']}"
        )
        inline_keyboard.append([detail_button, delete_button])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def generate_slots_keyboard(slots):
    """
    Генерация inline-клавиатуры для списка слотов в 2 ряда.
    :param slots: Список объектов LunchSlot.
    :return: InlineKeyboardMarkup.
    """
    inline_keyboard = []
    row = []
    for slot in slots:
        # Форматируем дату и время
        weekday = WEEKDAY_SHORTCUTS[slot.date.strftime("%A").lower()]
        month = MONTH_SHORTCUTS[slot.date.strftime("%m")]
        formatted_date = f"{weekday}, {slot.date.day} {month}"
        formatted_time = slot.start_time.strftime("%H:%M")
        button_text = f"{formatted_date}, {formatted_time}"

        # Добавляем кнопку в строку
        row.append(InlineKeyboardButton(text=button_text, callback_data=f"select_slot:{slot.id}"))

        # Если в строке 2 кнопки, добавляем её в клавиатуру
        if len(row) == 2:
            inline_keyboard.append(row)
            row = []

    # Добавляем оставшиеся кнопки, если они есть
    if row:
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

