from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user_states import UserCreationStates
from db.crud import create_user, get_all_users, save_registration_request
from db.database import SessionLocal
from keyboards.admin import role_selection_keyboard
from utils.common import return_to_main_menu

router = Router()

@router.message(F.text == "Заявка на регистрацию")
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Введите вашу фамилию:")
    await state.set_state(UserCreationStates.waiting_for_last_name)

@router.message(UserCreationStates.waiting_for_last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Введите ваше имя:")
    await state.set_state(UserCreationStates.waiting_for_first_name)

@router.message(UserCreationStates.waiting_for_first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Введите ваше отчество (или напишите 'нет', если отчество отсутствует):")
    await state.set_state(UserCreationStates.waiting_for_middle_name)

@router.message(UserCreationStates.waiting_for_middle_name)
async def get_middle_name(message: Message, state: FSMContext):
    middle_name = message.text if message.text.lower() != "нет" else None
    await state.update_data(middle_name=middle_name)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(UserCreationStates.waiting_for_phone_number)

@router.message(UserCreationStates.waiting_for_phone_number)
async def get_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Введите ваш email (обязательно):")
    await state.set_state(UserCreationStates.waiting_for_email)

@router.message(UserCreationStates.waiting_for_email)
async def get_email(message: Message, state: FSMContext):
    email = message.text
    if "@" not in email or "." not in email:
        await message.answer("Пожалуйста, введите корректный email.")
        return
    await state.update_data(email=email)
    await state.update_data(telegram_id=message.from_user.id)  # Сохраняем Telegram ID
    await message.answer("Выберите вашу роль:", reply_markup=role_selection_keyboard())
    await state.set_state(UserCreationStates.waiting_for_role)

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
    user_data["role"] = role

    # Сохраняем заявку в базе данных
    with SessionLocal() as session:
        save_registration_request(session, user_data)

    # Уведомляем администраторов
    admins = get_all_users()
    admin_ids = [admin.telegram_id for admin in admins if admin.role == "admin"]

    for admin_id in admin_ids:
        await callback_query.bot.send_message(
            admin_id,
            f"Поступила заявка на регистрацию:\n"
            f"Фамилия: {user_data['last_name']}\n"
            f"Имя: {user_data['first_name']}\n"
            f"Отчество: {user_data['middle_name'] or 'Не указано'}\n"
            f"Телефон: {user_data['phone_number']}\n"
            f"Email: {user_data['email']}\n"
            f"Роль: {user_data['role']}\n"
            f"Telegram ID: {user_data['telegram_id']}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Зарегистрировать", callback_data=f"approve:{user_data['telegram_id']}")],
                    [InlineKeyboardButton(text="Отклонить", callback_data=f"reject:{user_data['telegram_id']}")]
                ]
            )
        )

    await callback_query.message.answer("Ваша заявка отправлена на рассмотрение администраторам.")
    await state.clear()