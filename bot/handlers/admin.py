from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from db.crud import add_user

# Роутер бота для админ-команд
router = Router()

# Машина состояний (FSM) — для пошагового ввода пользователя
class AddUserFSM(StatesGroup):
    username = State()  # Ввод username
    phone = State()     # Ввод телефона
    role = State()      # Ввод роли

# Главная клавиатура с кнопкой "Добавить пользователя"
main_admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить пользователя")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие:"
)

# Клавиатура для выбора роли
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="admin")],
        [KeyboardButton(text="manager")],
        [KeyboardButton(text="employee")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,  # Клавиатура автоматически скрывается после выбора
    input_field_placeholder="Выберите роль:"
)

# Хэндлер для стартового сообщения (например, после /start)
@router.message(F.text == "/start")
async def admin_start(message: Message):
    await message.answer(
        "Добро пожаловать! Выберите действие:",
        reply_markup=main_admin_keyboard
    )

# Хэндлер при нажатии на кнопку "Добавить пользователя"
@router.message(F.text == "➕ Добавить пользователя")
async def add_user_cmd(message: Message, state: FSMContext):
    await message.answer("Введите username:")
    await state.set_state(AddUserFSM.username)

# Получение username
@router.message(AddUserFSM.username)
async def get_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(AddUserFSM.phone)

# Получение телефона
@router.message(AddUserFSM.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)

    # Показываем клавиатуру с выбором ролей
    await message.answer(
        "Выберите роль:",
        reply_markup=role_keyboard
    )
    await state.set_state(AddUserFSM.role)

# Получение роли и сохранение данных
@router.message(AddUserFSM.role)
async def save_user(message: Message, state: FSMContext):
    data = await state.get_data()

    # Сохраняем данные пользователя
    await add_user(
        telegram_id=str(message.from_user.id),
        username=data["username"],
        phone=data["phone"],
        role=message.text
    )

    # Уведомляем об успехе и возвращаем основную клавиатуру
    await message.answer(
        "✅ Пользователь добавлен.",
        reply_markup=main_admin_keyboard
    )
    await state.clear()
    