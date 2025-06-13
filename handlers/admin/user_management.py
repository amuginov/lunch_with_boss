from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import UserCreationStates, UserDeletionStates
from keyboards.admin import admin_keyboard
from utils.common import return_to_main_menu
from services.user_service import add_user, list_all_users, remove_user  # Импортируем сервисные функции

router = Router()

@router.message(F.text == "Добавить пользователя")
async def start_user_creation(message: Message, state: FSMContext):
    await message.answer("Введите Telegram ID нового пользователя:")
    await state.set_state(UserCreationStates.waiting_for_telegram_id)

@router.message(UserCreationStates.waiting_for_telegram_id)
async def get_telegram_id(message: Message, state: FSMContext):
    try:
        telegram_id = int(message.text)
        await state.update_data(telegram_id=telegram_id)
        await message.answer("Введите полное имя пользователя:")
        await state.set_state(UserCreationStates.waiting_for_full_name)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный Telegram ID (число).")

@router.message(UserCreationStates.waiting_for_full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите номер телефона пользователя:")
    await state.set_state(UserCreationStates.waiting_for_phone_number)

@router.message(UserCreationStates.waiting_for_phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="admin"), KeyboardButton(text="user"), KeyboardButton(text="manager")],
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите роль пользователя:", reply_markup=keyboard)
    await state.set_state(UserCreationStates.waiting_for_role)

@router.message(UserCreationStates.waiting_for_role)
async def get_role(message: Message, state: FSMContext):
    try:
        role = message.text.lower()
        if role not in ["admin", "user", "manager"]:
            await message.answer("Пожалуйста, выберите роль из предложенных вариантов: admin, user, manager.")
            return

        user_data = await state.get_data()

        # Используем сервис для добавления пользователя
        await add_user(
            telegram_id=user_data["telegram_id"],
            full_name=user_data["full_name"],
            phone_number=user_data["phone_number"],
            role=role
        )

        await message.answer("Пользователь успешно добавлен!")
        await return_to_main_menu(message, "admin", admin_keyboard())
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
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
            [f"ID: {user.telegram_id}, ФИО: {user.full_name}, Телефон: {user.phone_number or 'Не указан'}, Роль: {user.role}" for user in users]
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