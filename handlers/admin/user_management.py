from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.crud import create_user
from states.user_states import UserCreationStates

router = Router()

@router.message(F.text == "Управление пользователями")
async def manage_users(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить пользователя")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)

@router.message(F.text == "Добавить пользователя")
async def start_user_creation(message: Message, state: FSMContext):
    await message.answer("Введите полное имя пользователя:")
    await state.set_state(UserCreationStates.waiting_for_full_name)

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
    user_data = await state.get_data()
    create_user(
        telegram_id=message.from_user.id,
        full_name=user_data["full_name"],
        phone_number=user_data["phone_number"],
        role=message.text
    )
    await message.answer("Пользователь успешно добавлен!")
    await state.clear()