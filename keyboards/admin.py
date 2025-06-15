from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить пользователя")],
            [KeyboardButton(text="Список пользователей")],
            [KeyboardButton(text="Удалить пользователя")],  # Новая кнопка
            [KeyboardButton(text="Настройки")]
        ],
        resize_keyboard=True
    )

def role_selection_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Администратор", callback_data="role_admin")],
            [InlineKeyboardButton(text="Менеджер", callback_data="role_manager")],
            [InlineKeyboardButton(text="Пользователь", callback_data="role_user")],
        ]
    )
