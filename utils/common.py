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

from aiogram.types import ReplyKeyboardMarkup

async def return_to_main_menu(message, user_role, keyboard):
    """
    Обновляет ReplyKeyboardMarkup для пользователя путем отправки нового сообщения.
    :param message: Объект сообщения.
    :param user_role: Роль пользователя (manager, admin, employee).
    :param keyboard: Клавиатура для роли пользователя.
    """
    print(f"Keyboard type: {type(keyboard)}")  # Отладочный вывод
    if isinstance(keyboard, ReplyKeyboardMarkup):
        await message.answer("Возвращаюсь в главное меню...", reply_markup=keyboard)
    else:
        raise ValueError(f"Для обновления клавиатуры требуется объект ReplyKeyboardMarkup, получен: {type(keyboard)}")