from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from states.user_states import UserCreationStates, UserDeletionStates
from keyboards.admin import admin_keyboard
from utils.common import return_to_main_menu
from services.user_service import add_user, list_all_users, remove_user  # Импортируем сервисные функции

router = Router()

@router.message(F.text == "Добавить пользователя")
async def start_user_creation(message: Message, state: FSMContext):
    await message.answer("Введите фамилию нового пользователя:")
    await state.set_state(UserCreationStates.waiting_for_last_name)

@router.message(UserCreationStates.waiting_for_last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите имя нового пользователя:")
    await state.set_state(UserCreationStates.waiting_for_first_name)

@router.message(UserCreationStates.waiting_for_first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите отчество нового пользователя (или напишите 'нет', если отчество отсутствует):")
    await state.set_state(UserCreationStates.waiting_for_middle_name)

@router.message(UserCreationStates.waiting_for_middle_name)
async def get_middle_name(message: Message, state: FSMContext):
    middle_name = message.text if message.text.lower() != "нет" else None
    await state.update_data(middle_name=middle_name)
    await message.answer("Введите номер телефона нового пользователя:")
    await state.set_state(UserCreationStates.waiting_for_phone_number)

@router.message(UserCreationStates.waiting_for_phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Введите email нового пользователя:")
    await state.set_state(UserCreationStates.waiting_for_email)

@router.message(UserCreationStates.waiting_for_email)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите Telegram ID нового пользователя:")
    await state.set_state(UserCreationStates.waiting_for_telegram_id)

@router.message(UserCreationStates.waiting_for_telegram_id)
async def get_telegram_id(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text)
        await state.update_data(telegram_id=telegram_id)

        # Создаём inline-клавиатуру для выбора роли
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Администратор", callback_data="role_admin")],
                [InlineKeyboardButton(text="Менеджер", callback_data="role_manager")],
                [InlineKeyboardButton(text="Пользователь", callback_data="role_user")],
            ]
        )
        await message.answer("Выберите роль пользователя:", reply_markup=keyboard)
        await state.set_state(UserCreationStates.waiting_for_role)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный Telegram ID (число).")

@router.callback_query(UserCreationStates.waiting_for_role)
async def get_role(callback_query: CallbackQuery, state: FSMContext):
    role_mapping = {
        "role_admin": "admin",
        "role_manager": "manager",
        "role_user": "user"
    }
    role = role_mapping.get(callback_query.data)

    if not role:
        await callback_query.message.answer("Пожалуйста, выберите роль из предложенных вариантов.")
        return

    user_data = await state.get_data()

    # Используем сервис для добавления пользователя
    await add_user(
        telegram_id=user_data["telegram_id"],
        last_name=user_data["last_name"],
        first_name=user_data["first_name"],
        middle_name=user_data["middle_name"],
        phone_number=user_data["phone_number"],
        email=user_data["email"],
        role=role
    )

    await callback_query.message.answer("Пользователь успешно добавлен!")
    await return_to_main_menu(callback_query.message, "admin", admin_keyboard())
    await state.clear()

@router.message(F.text == "Список пользователей")
async def list_users(message: Message):
    try:
        # Используем сервис для получения списка пользователей
        users = await list_all_users()

        if not users:
            await message.answer("Список пользователей пуст.")
            return

        user_list = "\n".join(
            [f"ID: {user.telegram_id}, Фамилия: {user.last_name}, Имя: {user.first_name}, Отчество: {user.middle_name or 'Не указано'}, Телефон: {user.phone_number or 'Не указан'}, Email: {user.email or 'Не указан'}, Роль: {user.role}" for user in users]
        )
        await message.answer(f"Список пользователей:\n\n{user_list}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении списка пользователей: {e}")

@router.message(F.text == "Удалить пользователя")
async def start_user_deletion(message: Message, state: FSMContext):
    await message.answer("Введите Telegram ID пользователя, которого вы хотите удалить:")
    await state.set_state(UserDeletionStates.waiting_for_telegram_id)

@router.message(UserDeletionStates.waiting_for_telegram_id)
async def delete_user(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text)

        # Используем сервис для удаления пользователя
        await remove_user(telegram_id)

        await message.answer(f"Пользователь с Telegram ID {telegram_id} успешно удален!")
        await return_to_main_menu(message, "admin", admin_keyboard())
        await state.clear()
    except ValueError as e:
        await message.answer(str(e))
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка при удалении пользователя: {e}")
        await state.clear()