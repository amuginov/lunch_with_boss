from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.user_states import LunchSlotCreationStates
from keyboards.manager import manager_keyboard, generate_date_inline_keyboard, generate_time_inline_keyboard, generate_slots_keyboard
from utils.common import return_to_main_menu
from services.schedule_service import (
    get_manager_slots,
    add_lunch_slot,
    get_slot_details,
    remove_lunch_slot,
)
from datetime import datetime
from db.crud import get_user_by_telegram_id  # Импортируем функцию

router = Router()

@router.message(Command(commands=["schedule"]))
async def schedule_command(message: Message):
    await message.answer("Здесь вы можете управлять расписанием.")

@router.message(F.text == "📅 Управление слотами обедов")
async def start_lunch_slot_creation(message: Message, state: FSMContext):
    await message.answer("Выберите дату слота:", reply_markup=generate_date_inline_keyboard())
    await state.set_state(LunchSlotCreationStates.waiting_for_date)

@router.message(F.text == "📅 Новый слот")
async def start_lunch_slot_creation(message: Message, state: FSMContext):
    await message.answer("Выберите дату слота:", reply_markup=generate_date_inline_keyboard())
    await state.set_state(LunchSlotCreationStates.waiting_for_date)

@router.message(F.text == "📋 Мои слоты")
async def view_slots(message: Message):
    user = get_user_by_telegram_id(message.from_user.id)  # Убрали await
    if not user or user.role != "manager":
        await message.answer("У вас нет доступа к этому функционалу.")
        return

    manager_slots = await get_manager_slots(user.id)

    if not manager_slots:
        await message.answer("У вас нет активных слотов.")
        return

    keyboard = generate_slots_keyboard(manager_slots)
    await message.answer("Ваши слоты:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("select_date:"))
async def get_date(callback: CallbackQuery, state: FSMContext):
    try:
        slot_date = datetime.strptime(callback.data.split(":")[1], "%Y-%m-%d").date()
        await state.update_data(date=slot_date)
        await callback.message.answer("Выберите время начала слота:", reply_markup=generate_time_inline_keyboard())
        await state.set_state(LunchSlotCreationStates.waiting_for_time)
    except ValueError as e:
        await callback.message.answer("Неверный формат даты. Попробуйте снова, выбрав дату из кнопок.")


@router.callback_query(F.data.startswith("select_time:"))
async def get_time(callback: CallbackQuery, state: FSMContext):
    try:
        time_data = ":".join(callback.data.split(":")[1:])
        start_time = datetime.strptime(time_data, "%H:%M").time()

        slot_data = await state.get_data()
        if "date" not in slot_data:
            await callback.message.answer("Ошибка: дата не была выбрана. Попробуйте снова.")
            return

        user = get_user_by_telegram_id(callback.from_user.id)  # Убрали await
        if not user:
            await callback.message.answer("Вы не авторизованы.")
            return

        # Пытаемся создать слот
        try:
            await add_lunch_slot(
                date=slot_data["date"],
                start_time=start_time,
                manager_id=user.id
            )
            await callback.message.answer("Слот успешно добавлен!")
        except ValueError as e:
            await callback.message.answer(f"Ошибка: {e}")

        await return_to_main_menu(callback.message, "manager", manager_keyboard())
        await state.clear()
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {e}")


@router.callback_query(F.data.startswith("slot_detail:"))
async def slot_details(callback: CallbackQuery):
    slot_id = int(callback.data.split(":")[1])

    try:
        slot = await get_slot_details(slot_id)

        formatted_date = slot.date.strftime("%A, %d %B")
        formatted_time = slot.start_time.strftime("%H:%M")
        response = (
            f"Детали слота:\n"
            f"- День недели: {formatted_date}\n"
            f"- Время: {formatted_time}\n"
            f"- Менеджер: {slot.manager.full_name}"
        )
        await callback.message.answer(response)
    except ValueError as e:
        await callback.message.answer(str(e))
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при получении деталей слота: {e}")


@router.callback_query(F.data.startswith("delete_slot:"))
async def delete_slot(callback: CallbackQuery):
    slot_id = int(callback.data.split(":")[1])

    try:
        await remove_lunch_slot(slot_id)
        await callback.message.answer("Слот успешно удалён.")
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении слота: {e}")