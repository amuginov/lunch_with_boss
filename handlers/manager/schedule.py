from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.user_states import LunchSlotCreationStates
from db.crud import create_lunch_slot, get_user_by_telegram_id
from keyboards.manager import generate_date_keyboard, generate_time_keyboard
from datetime import datetime

router = Router()

@router.message(Command(commands=["schedule"]))
async def schedule_command(message: Message):
    await message.answer("Здесь вы можете управлять расписанием.")

@router.message(F.text == "📅 Управление слотами обедов")
async def start_lunch_slot_creation(message: Message, state: FSMContext):
    await message.answer("Выберите дату слота:", reply_markup=generate_date_keyboard())
    await state.set_state(LunchSlotCreationStates.waiting_for_date)

@router.message(LunchSlotCreationStates.waiting_for_date)
async def get_date(message: Message, state: FSMContext):
    try:
        # Преобразуем текст кнопки в дату
        slot_date = datetime.strptime(message.text, "%A, %d %B").date()
        await state.update_data(date=slot_date)
        await message.answer("Выберите время начала слота:", reply_markup=generate_time_keyboard())
        await state.set_state(LunchSlotCreationStates.waiting_for_time)
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте снова, выбрав дату из кнопок.")

@router.message(LunchSlotCreationStates.waiting_for_time)
async def get_time(message: Message, state: FSMContext):
    try:
        # Преобразуем текст кнопки в время
        start_time = datetime.strptime(message.text, "%H:%M").time()
        slot_data = await state.get_data()

        # Получаем пользователя из базы данных
        user = get_user_by_telegram_id(message.from_user.id)
        if not user or user.role != "manager":
            await message.answer("Вы не авторизованы как менеджер.")
            return

        # Создаем слот
        create_lunch_slot(
            date=slot_data["date"],
            start_time=start_time,
            manager_id=user.id  # Привязка к менеджеру
        )
        await message.answer("Слот успешно добавлен!")
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат времени. Попробуйте снова, выбрав время из кнопок.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        await state.clear()