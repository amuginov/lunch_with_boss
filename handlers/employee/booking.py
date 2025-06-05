from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import LunchBookingStates
from db.crud import get_all_users, get_all_lunch_slots
from db.database import SessionLocal  # Импортируем SessionLocal
from db.models import LunchSlot, User  # Импортируем LunchSlot и User
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()

@router.message(F.text == "🍽 Забронировать обед")
async def start_booking(message: Message, state: FSMContext):
    """
    Начало процесса бронирования обеда.
    """
    # Получаем список менеджеров
    managers = [user for user in get_all_users() if user.role == "manager"]

    if not managers:
        await message.answer("Нет доступных менеджеров для бронирования.")
        return

    # Генерируем кнопки с менеджерами
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=manager.full_name)] for manager in managers],
        resize_keyboard=True
    )

    await message.answer("С кем Вы хотите забронировать обед?", reply_markup=keyboard)
    await state.set_state(LunchBookingStates.waiting_for_manager)


@router.message(LunchBookingStates.waiting_for_manager)
async def choose_manager(message: Message, state: FSMContext):
    """
    Обработка выбора менеджера.
    """
    # Сохраняем выбранного менеджера
    selected_manager = message.text
    await state.update_data(manager=selected_manager)

    # Получаем список свободных слотов для выбранного менеджера
    all_slots = get_all_lunch_slots()
    available_slots = [
        slot for slot in all_slots
        if slot.manager.full_name == selected_manager and not slot.is_booked
    ]

    if not available_slots:
        await message.answer("Нет доступных слотов для бронирования.")
        await state.clear()
        return

    # Генерируем кнопки с доступными слотами
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{slot.date} {slot.start_time}")] for slot in available_slots],
        resize_keyboard=True
    )

    await message.answer("Выберите слот для бронирования:", reply_markup=keyboard)
    await state.set_state(LunchBookingStates.waiting_for_slot)


@router.message(LunchBookingStates.waiting_for_slot)
async def book_slot(message: Message, state: FSMContext):
    """
    Обработка выбора слота.
    """
    selected_slot = message.text
    slot_data = await state.get_data()

    # Обновляем статус слота в базе данных
    with SessionLocal() as session:
        # Получаем ID менеджера по имени
        manager = session.query(User).filter(User.full_name == slot_data["manager"]).first()
        if not manager:
            await message.answer("Менеджер не найден.")
            await state.clear()
            return

        # Фильтруем слот по дате, времени и ID менеджера
        slot = session.query(LunchSlot).filter(
            LunchSlot.date == selected_slot.split()[0],
            LunchSlot.start_time == selected_slot.split()[1],
            LunchSlot.manager_id == manager.id
        ).first()

        if slot:
            slot.is_booked = True
            session.commit()
            await message.answer(f"Вы успешно забронировали обед с менеджером {slot_data['manager']} на {selected_slot}.")
        else:
            await message.answer("Слот не найден или уже забронирован.")

    await state.clear()