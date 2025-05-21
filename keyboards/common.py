from keyboards.admin import admin_keyboard
from keyboards.manager import manager_keyboard
from keyboards.employee import employee_keyboard
from aiogram.types import ReplyKeyboardMarkup

def main_menu_keyboard(role: str) -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру по роли пользователя,
    используя отдельные модули клавиатур.
    """
    if role == "admin":
        return admin_keyboard()
    elif role == "manager":
        return manager_keyboard()
    elif role == "employee":
        return employee_keyboard()
    else:
        # Если роль неизвестна — возвращаем пустую клавиатуру
        return ReplyKeyboardMarkup(resize_keyboard=True)
