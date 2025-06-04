from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.user_states import LunchSlotCreationStates
from db.crud import create_lunch_slot
from datetime import datetime

router = Router()

@router.message(Command(commands=["schedule"]))
async def schedule_command(message: Message):
    await message.answer("Здесь вы можете управлять расписанием.")

@router.message(F.text == "📅 Управление слотами обедов")
async def start_lunch_slot_creation(message: Message, state: FSMContext):
    await message.answer("Введите дату слота в формате ГГГГ-ММ-ДД:")
    await state.set_state(LunchSlotCreationStates.waiting_for_date)

@router.message(LunchSlotCreationStates.waiting_for_date)
async def get_date(message: Message, state: FSMContext):
    try:
        slot_date = datetime.strptime(message.text, "%Y-%m-%d").date()
        await state.update_data(date=slot_date)
        await message.answer("Введите время начала слота в формате ЧЧ:ММ:")
        await state.set_state(LunchSlotCreationStates.waiting_for_start_time)
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте снова (ГГГГ-ММ-ДД).")

@router.message(LunchSlotCreationStates.waiting_for_start_time)
async def get_start_time(message: Message, state: FSMContext):
    try:
        start_time = datetime.strptime(message.text, "%H:%M").time()
        slot_data = await state.get_data()

        # Создаем слот
        create_lunch_slot(
            date=slot_data["date"],
            start_time=start_time
        )
        await message.answer("Слот успешно добавлен!")
        await state.clear()
    except ValueError:
        await message.answer("Неверный формат времени. Попробуйте снова (ЧЧ:ММ).")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        await state.clear()