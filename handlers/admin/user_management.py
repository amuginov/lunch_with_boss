
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.filters import StateFilter
from db.crud import add_user, get_all_users, delete_user

# Роутер для админских команд
router = Router()

# FSM — машина состояний для добавления пользователя (пошаговый ввод)
class AddUserFSM(StatesGroup):
    username = State()  # Запрос username
    phone = State()     # Запрос телефона
    role = State()      # Запрос роли (admin/manager/employee)

# Состояние для удаления пользователя
class DeleteUserFSM(StatesGroup):
    username = State()  # Состояние ожидания username

# Клавиатура с кнопками для главного меню админа
main_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить пользователя")],
        [KeyboardButton(text="🗑 Удалить пользователя")],
        [KeyboardButton(text="📋 Список пользователей")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

# Клавиатура для выбора роли пользователя при добавлении
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="admin")],
        [KeyboardButton(text="manager")],
        [KeyboardButton(text="employee")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите роль"
)

# Обработчик команды /start для администратора
@router.message(F.text == "/start")
async def admin_start(message: Message):
    await message.answer(
        "Добро пожаловать в админ-панель! Выберите действие:",
        reply_markup=main_admin_keyboard
    )

# Обработчик нажатия "➕ Добавить пользователя" — старт FSM для добавления
@router.message(F.text == "➕ Добавить пользователя")
async def add_user_cmd(message: Message, state: FSMContext):
    await message.answer("Введите username пользователя:")
    await state.set_state(AddUserFSM.username)

# Получение username — следующий шаг FSM
@router.message(StateFilter(AddUserFSM.username))
async def get_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(AddUserFSM.phone)

# Получение телефона
@router.message(StateFilter(AddUserFSM.phone))
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "Выберите роль пользователя:",
        reply_markup=role_keyboard
    )
    await state.set_state(AddUserFSM.role)

# Получение роли, сохранение пользователя в базу, завершение FSM
@router.message(StateFilter(AddUserFSM.role))
async def save_user(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_user(
        telegram_id=str(message.from_user.id),
        username=data["username"],
        phone=data["phone"],
        role=message.text
    )
    await message.answer("✅ Пользователь успешно добавлен.", reply_markup=main_admin_keyboard)
    await state.clear()

# Обработчик кнопки "📋 Список пользователей"
@router.message(F.text == "📋 Список пользователей")
async def list_users(message: Message):
    users = await get_all_users()
    if not users:
        await message.answer("Пользователей пока нет.")
        return
    response = "📋 Список пользователей:\n\n"
    for user in users:
        response += f"👤 {user.username} | 📞 {user.phone} | 🛡 {user.role}\n"
    await message.answer(response)

# Обработчик кнопки "🗑 Удалить пользователя" — начало удаления
@router.message(F.text == "🗑 Удалить пользователя")
async def delete_user_start(message: Message, state: FSMContext):
    await message.answer("Введите username пользователя для удаления:")
    await state.set_state(DeleteUserFSM.username)

# Получение username для удаления, удаление из БД
@router.message(StateFilter(DeleteUserFSM.username))
async def process_delete_user(message: Message, state: FSMContext):
    username = message.text
    await delete_user(username)
    await message.answer(f"Пользователь @{username} удалён, если он существовал.", reply_markup=main_admin_keyboard)
    await state.clear()
