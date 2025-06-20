from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить пользователя")],
            [KeyboardButton(text="Список пользователей")],
            [KeyboardButton(text="Удалить пользователя")],
            [KeyboardButton(text="Помощь")],
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

def manager_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Новый слот"), KeyboardButton(text="📋 Мои слоты")],
            [KeyboardButton(text="❓ Помощь")],  # Добавляем кнопку "Помощь"
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )

def employee_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🍽 Забронировать обед")],
            [KeyboardButton(text="📋 Мои бронирования")],
            [KeyboardButton(text="Помощь")],  # Добавляем кнопку "Помощь"
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие:"
    )
