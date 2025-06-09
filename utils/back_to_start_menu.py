from aiogram.types import ReplyKeyboardMarkup
from keyboards.manager import manager_keyboard
from keyboards.admin import admin_keyboard
from keyboards.employee import employee_keyboard

async def return_to_main_menu(message, user_role):
    """
    Возвращает пользователя в главное меню в зависимости от его роли.
    :param message: Объект сообщения.
    :param user_role: Роль пользователя (manager, admin, employee).
    """
    if user_role == "manager":
        await message.answer("Возвращаюсь в главное меню.", reply_markup=manager_keyboard())
    elif user_role == "admin":
        await message.answer("Возвращаюсь в главное меню.", reply_markup=admin_keyboard())
    elif user_role == "employee":
        await message.answer("Возвращаюсь в главное меню.", reply_markup=employee_keyboard())
    else:
        await message.answer("Ваша роль не поддерживается.")