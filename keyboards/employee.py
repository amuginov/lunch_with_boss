from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        if not booking.manager:
            print(f"Ошибка: Поле 'manager' пустое для бронирования ID={booking.id}")
            continue

        print(f"Менеджер: {booking.manager.full_name}")

        # Форматируем дату и время
        formatted_date = booking.date.strftime("%A, %d %B")
        formatted_time = booking.start_time.strftime("%H:%M")
        button_text = f"{formatted_date}, {formatted_time}, {booking.manager.full_name}"

        # Кнопка для деталей бронирования
        detail_button = InlineKeyboardButton(
            text=button_text,
            callback_data=f"detail_booking:{booking.id}"
        )
        # Кнопка для удаления бронирования
        delete_button = InlineKeyboardButton(
            text="Удалить бронь",
            callback_data=f"delete_booking:{booking.id}"
        )
        inline_keyboard.append([detail_button, delete_button])  # Добавляем кнопки в список

        # Отладочное сообщение после добавления кнопок
        print(f"Добавлены кнопки для бронирования ID={booking.id}: {inline_keyboard}")

    # Создаём объект InlineKeyboardMarkup с явным указанием inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    print(f"Сгенерированная клавиатура: {keyboard.inline_keyboard}")
    return keyboard