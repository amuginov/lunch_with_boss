from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from db.crud import create_user
from states.user_states import UserCreationStates

router = Router()

@router.message(F.text == "Добавить пользователя")
async def start_user_creation(message: Message, state: FSMContext):
    # Сохраняем telegram_id текущего пользователя
    await state.update_data(telegram_id=message.from_user.id)
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
    try:
        role = message.text.lower()
        if role not in ["admin", "user", "manager"]:
            await message.answer("Пожалуйста, выберите роль из предложенных вариантов: admin, user, manager.")
            return

        # Получаем данные из состояния
        user_data = await state.get_data()

        # Логируем данные для проверки
        print(f"Создание пользователя с данными: Telegram ID={user_data['telegram_id']}, "
              f"Full Name={user_data['full_name']}, Phone={user_data['phone_number']}, Role={role}")

        # Создаем пользователя
        create_user(
            telegram_id=user_data["telegram_id"],  # Используем telegram_id из состояния
            full_name=user_data["full_name"],
            phone_number=user_data["phone_number"],
            role=role
        )

        await message.answer("Пользователь успешно добавлен!")
        await state.clear()
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        await state.clear()