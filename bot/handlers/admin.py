from aiogram import Router, F
from aiogram.types import Message
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

# Обработка команды /add_user
@router.message(F.text == "/add_user")
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
    await message.answer("Введите роль (admin / manager / employee):")
    await state.set_state(AddUserFSM.role)

# Получение роли и сохранение данных
@router.message(AddUserFSM.role)
async def save_user(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_user(
        telegram_id=str(message.from_user.id),
        username=data["username"],
        phone=data["phone"],
        role=message.text
    )
    await message.answer("Пользователь добавлен.")
    await state.clear()
