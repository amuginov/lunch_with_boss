from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Словари для сокращения дней недели и месяцев
WEEKDAY_SHORTCUTS = {
    "понедельник": "пн",
    "вторник": "вт",
    "среда": "ср",
    "четверг": "чт",
    "пятница": "пт",
    "суббота": "сб",
    "воскресенье": "вс",
}

MONTH_SHORTCUTS = {
    "01": "янв",
    "02": "фев",
    "03": "март",
    "04": "апр",
    "05": "май",
    "06": "июн",
    "07": "июл",
    "08": "авг",
    "09": "сен",
    "10": "окт",
    "11": "ноя",
    "12": "дек",
}

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

def generate_booking_keyboard(bookings):
    """
    Генерация клавиатуры для списка бронирований.
    :param bookings: Список объектов LunchSlot.
    :return: InlineKeyboardMarkup.
    """
    print(f"Переданные бронирования: {bookings}")
    inline_keyboard = []  # Явно создаём список для кнопок
    for booking in bookings:
        # Вывод данных для отладки
        print(f"Обработка бронирования: ID={booking.id}, дата={booking.date}, время={booking.start_time}")

        # Сокращаем день недели и месяц
        weekday = WEEKDAY_SHORTCUTS[booking.date.strftime("%A")]
        month = MONTH_SHORTCUTS[booking.date.strftime("%m")]  # Получаем номер месяца и сопоставляем с сокращением
        formatted_date = f"{weekday}, {booking.date.day} {month}"
        formatted_time = booking.start_time.strftime("%H:%M")
        button_text = f"{formatted_date}, {formatted_time}, {booking.manager.full_name}"

        # Кнопка для деталей бронирования
        detail_button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"detail_booking:{booking.id}"
        )
        # Кнопка для удаления бронирования
        delete_button = InlineKeyboardButton(
            text="❌",  # Используем символ вместо текста для минимального размера
            callback_data=f"delete_booking:{booking.id}"
        )
        inline_keyboard.append([detail_button, delete_button])  # Оставляем кнопки на одной строке

        # Отладочное сообщение после добавления кнопок
        print(f"Добавлены кнопки для бронирования ID={booking.id}: {inline_keyboard}")

    # Создаём объект InlineKeyboardMarkup с явным указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    print(f"Сгенерированная клавиатура: {keyboard.inline_keyboard}")
    return keyboard