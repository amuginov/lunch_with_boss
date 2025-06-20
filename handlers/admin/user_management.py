from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from states.user_states import UserCreationStates, UserDeletionStates
from keyboards.admin import admin_keyboard
from keyboards.manager import manager_keyboard
from keyboards.employee import employee_keyboard
from utils.common import return_to_main_menu
from services.user_service import add_user, list_all_users, remove_user, get_all_users  # Импортируем сервисные функции
from services.registration_service import approve_registration, reject_registration  # Исправленный импорт
from db.crud import get_user_by_telegram_id, get_registration_request_by_telegram_id, delete_registration_request, get_user_by_telegram_id_with_session  # Исправленный импорт
from db.database import SessionLocal

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
        await state.clear()
    except ValueError as e:
        await message.answer(str(e))
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка при удалении пользователя: {e}")
        await state.clear()

@router.callback_query(F.data.startswith("approve:"))
async def approve_user(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split(":")[1])

    # Получаем данные заявки из базы данных
    with SessionLocal() as session:
        user_data = get_registration_request_by_telegram_id(session, telegram_id)

    if not user_data:
        await callback_query.message.answer("Ошибка: Заявка на регистрацию не найдена.")
        return

    try:
        # Регистрируем пользователя
        await approve_registration({
            "telegram_id": user_data.telegram_id,
            "last_name": user_data.last_name,
            "first_name": user_data.first_name,
            "middle_name": user_data.middle_name,
            "phone_number": user_data.phone_number,
            "email": user_data.email,
            "role": user_data.role
        })

        # Удаляем заявку из базы данных
        with SessionLocal() as session:
            delete_registration_request(session, telegram_id)

        await callback_query.message.answer(f"Пользователь {user_data.last_name} {user_data.first_name} успешно зарегистрирован.")
    except Exception as e:
        await callback_query.message.answer(f"Произошла ошибка при регистрации пользователя: {e}")

@router.callback_query(F.data.startswith("reject:"))
async def reject_user(callback_query: CallbackQuery):
    telegram_id = int(callback_query.data.split(":")[1])

    # Извлекаем данные заявки из базы данных
    with SessionLocal() as session:
        user_data = get_registration_request_by_telegram_id(session, telegram_id)

    if not user_data:
        await callback_query.message.answer(f"Ошибка: Заявка на регистрацию с Telegram ID {telegram_id} не найдена.")
        return

    try:
        # Удаляем заявку из базы данных
        with SessionLocal() as session:
            delete_registration_request(session, telegram_id)

        await callback_query.message.answer(f"Заявка пользователя {user_data.last_name} {user_data.first_name} отклонена.")

        # Отправляем сообщение пользователю
        await callback_query.bot.send_message(
            telegram_id,
            "Вам отказано в регистрации в чат-боте \"АЛРОСА обед\"."
        )

        # Уведомляем всех администраторов
        admins = get_all_users()
        admin_ids = [admin.telegram_id for admin in admins if admin.role == "admin"]
        for admin_id in admin_ids:
            await callback_query.bot.send_message(
                admin_id,
                f"Отклонена заявка пользователя:\n"
                f"Фамилия: {user_data.last_name}\n"
                f"Имя: {user_data.first_name}\n"
                f"Роль: {user_data.role}"
            )
    except Exception as e:
        await callback_query.message.answer(f"Произошла ошибка при отклонении заявки: {e}")