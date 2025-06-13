from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.user_states import LunchSlotCreationStates
from db.crud import create_lunch_slot, get_user_by_telegram_id, get_all_lunch_slots
from keyboards.manager import manager_keyboard, generate_date_inline_keyboard, generate_time_inline_keyboard, generate_slots_keyboard  # Импортируем manager_keyboard, generate_date_inline_keyboard, generate_time_inline_keyboard и generate_slots_keyboard
from keyboards.admin import admin_keyboard  # Импортируем admin_keyboard
from keyboards.employee import employee_keyboard  # Импортируем employee_keyboard
from datetime import datetime, timedelta
from utils.back_to_start_menu import return_to_main_menu
from db.models import LunchSlot
from db.database import SessionLocal

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
    """
    Обработка нажатия кнопки "📅 Новый слот".
    """
    await message.answer("Выберите дату слота:", reply_markup=generate_date_inline_keyboard())
    await state.set_state(LunchSlotCreationStates.waiting_for_date)

@router.message(F.text == "📋 Мои слоты")
async def view_slots(message: Message):
    """
    Отображение всех слотов менеджера в виде таблицы кнопок.
    """
    user = get_user_by_telegram_id(message.from_user.id)
    if not user or user.role != "manager":
        await message.answer("У вас нет доступа к этому функционалу.")
        return

    # Получаем все слоты менеджера, начиная с сегодняшнего дня
    all_slots = get_all_lunch_slots()
    today = datetime.now().date()
    manager_slots = [
        slot for slot in all_slots
        if slot.manager_id == user.id and slot.date >= today
    ]

    if not manager_slots:
        await message.answer("У вас нет активных слотов.")
        return

    # Генерируем клавиатуру со слотами
    keyboard = generate_slots_keyboard(manager_slots)
    await message.answer("Ваши слоты:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("select_date:"))
async def get_date(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора даты через Inline-кнопки.
    """
    try:
        # Логируем данные для диагностики
        print(f"Получено callback_data: {callback.data}")

        # Извлекаем дату из callback_data
        slot_date = datetime.strptime(callback.data.split(":")[1], "%Y-%m-%d").date()
        print(f"Преобразованная дата: {slot_date}")

        await state.update_data(date=slot_date)
        await callback.message.answer("Выберите время начала слота:", reply_markup=generate_time_inline_keyboard())
        await state.set_state(LunchSlotCreationStates.waiting_for_time)
    except ValueError as e:
        print(f"Ошибка преобразования даты: {e}")
        await callback.message.answer("Неверный формат даты. Попробуйте снова, выбрав дату из кнопок.")

@router.callback_query(F.data.startswith("select_time:"))
async def get_time(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора времени через Inline-кнопки.
    """
    try:
        # Логируем данные для диагностики
        print(f"Получено callback_data: {callback.data}")

        # Извлекаем время из callback_data
        time_data = ":".join(callback.data.split(":")[1:])  # Корректное извлечение времени
        print(f"Извлечённое время: {time_data}")

        start_time = datetime.strptime(time_data, "%H:%M").time()
        print(f"Преобразованное время: {start_time}")

        slot_data = await state.get_data()
        print(f"Данные состояния: {slot_data}")

        # Проверяем наличие ключа "date" в состоянии
        if "date" not in slot_data:
            await callback.message.answer("Ошибка: дата не была выбрана. Попробуйте снова.")
            return

        # Получаем пользователя из базы данных
        user = get_user_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.answer("Вы не авторизованы.")
            return

        # Проверяем на дублирование слота
        existing_slots = get_all_lunch_slots()
        for slot in existing_slots:
            if slot.date == slot_data["date"] and slot.start_time == start_time and slot.manager_id == user.id:
                await callback.message.answer("Выбранный слот Вы ранее уже открыли для записи. Попробуйте выбрать новый слот.")
                await state.clear()
                return

        # Создаем слот
        create_lunch_slot(
            date=slot_data["date"],
            start_time=start_time,
            manager_id=user.id  # Привязка к менеджеру
        )
        await callback.message.answer("Слот успешно добавлен!")

        # Используем функцию возврата в главное меню
        await return_to_main_menu(callback.message, user.role)

        await state.clear()
    except ValueError as e:
        print(f"Ошибка преобразования времени: {e}")
        await callback.message.answer("Неверный формат времени. Попробуйте снова, выбрав время из кнопок.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await callback.message.answer(f"Произошла ошибка: {e}")


@router.callback_query(F.data.startswith("slot_detail:"))
async def slot_details(callback: CallbackQuery):
    """
    Отображение деталей слота.
    """
    slot_id = int(callback.data.split(":")[1])

    with SessionLocal() as session:
        slot = session.query(LunchSlot).filter(LunchSlot.id == slot_id).first()
        if not slot:
            await callback.message.answer("Слот не найден.")
            return

        # Форматируем дату и время
        formatted_date = slot.date.strftime("%A, %d %B")
        formatted_time = slot.start_time.strftime("%H:%M")
        response = (
            f"Детали слота:\n"
            f"- День недели: {formatted_date}\n"
            f"- Время: {formatted_time}\n"
            f"- Менеджер: {slot.manager.full_name}"
        )
        await callback.message.answer(response)


@router.callback_query(F.data.startswith("delete_slot:"))
async def delete_slot(callback: CallbackQuery):
    """
    Удаление слота.
    """
    slot_id = int(callback.data.split(":")[1])

    with SessionLocal() as session:
        slot = session.query(LunchSlot).filter(LunchSlot.id == slot_id).first()
        if not slot:
            await callback.message.answer("Слот не найден.")
            return

        session.delete(slot)
        session.commit()

        await callback.message.answer("Слот успешно удалён.")