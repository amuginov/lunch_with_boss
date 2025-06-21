from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup
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
from db.crud import get_user_by_telegram_id, get_user_by_telegram_id_with_session  # Импортируем функции
from db.models import User  # Импортируем класс User
from db.database import SessionLocal  # Импортируем SessionLocal

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
    try:
        print(f"Received request from Telegram ID: {message.from_user.id}")  # Отладочный вывод

        # Создаём объект Session
        with SessionLocal() as session:
            # Получаем пользователя
            user = get_user_by_telegram_id_with_session(session, message.from_user.id)
            print(f"User: {user}")  # Отладочный вывод

            if not user or user.role != "manager":
                await message.answer("У вас нет доступа к этому функционалу.")
                return

            # Получаем слоты менеджера
            manager_slots = await get_manager_slots(user.id)
            print(f"Manager Slots: {manager_slots}")  # Отладочный вывод

            if not manager_slots:
                await message.answer("У вас нет активных слотов.")
                return

            # Генерируем клавиатуру для отображения слотов
            keyboard = generate_slots_keyboard(manager_slots)
            await message.answer("Ваши слоты:", reply_markup=keyboard)
    except Exception as e:
        print(f"Error in view_slots: {e}")  # Отладочный вывод
        await message.answer(f"Произошла ошибка: {e}")

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

        user = get_user_by_telegram_id(callback.from_user.id)
        print(f"Callback Telegram ID: {callback.from_user.id}, User: {user}, Role: {user.role}")  # Отладочный вывод
        print(f"Slot Data: {slot_data}, Start Time: {start_time}")  # Отладочный вывод

        # Уточнённая проверка объекта пользователя
        if user is None or user.role.strip() != "manager":
            await callback.message.answer(f"Ошибка: Пользователь с Telegram ID {callback.from_user.id} не найден или не имеет роли 'manager'.")
            return

        # Пытаемся создать слот
        try:
            slot = await add_lunch_slot(
                date=slot_data["date"],
                start_time=start_time,
                manager_id=user.id
            )
            print(f"Created Slot: {slot}")  # Отладочный вывод
            await callback.message.answer("Слот успешно добавлен! Событие добавлено в Ваш календарь. Не забудьте принять это приглашение в Вашем календаре.")
        except ValueError as e:
            await callback.message.answer(f"Ошибка: {e}")
        except Exception as e:
            await callback.message.answer(f"Произошла ошибка: {e}")

        await return_to_main_menu(callback.message, "manager", manager_keyboard())
        await state.clear()
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {e}")


@router.callback_query(F.data.startswith("slot_detail:"))
async def slot_details(callback: CallbackQuery):
    slot_id = int(callback.data.split(":")[1])

    try:
        slot = await get_slot_details(slot_id)
        print(f"Slot ID: {slot_id}, Slot: {slot}, Manager: {slot.manager if slot else 'None'}")  # Отладочный вывод

        if not slot:
            await callback.message.answer("Слот не найден.")
            return

        formatted_date = slot.date.strftime("%A, %d %B")
        formatted_time = slot.start_time.strftime("%H:%M")
        response = (
            f"Детали слота:\n"
            f"- День недели: {formatted_date}\n"
            f"- Время: {formatted_time}\n"
            f"- Менеджер: {slot.manager.last_name} {slot.manager.first_name}"
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
        print(f"Attempting to delete slot with ID: {slot_id}")  # Отладочный вывод
        await remove_lunch_slot(slot_id)
        await callback.message.answer("Слот успешно удалён. Событие удалено из Google Calendar.")
    except Exception as e:
        print(f"Error while deleting slot: {e}")  # Отладочный вывод
        await callback.message.answer(f"Произошла ошибка при удалении слота: {e}")


@router.callback_query(F.data.startswith("time:"))
async def select_time(callback_query: CallbackQuery):
    try:
        # Извлекаем Telegram ID пользователя
        telegram_id = callback_query.from_user.id

        # Получаем пользователя из базы данных
        user = get_user_by_telegram_id(callback_query.from_user.id)

        if not user:
            await callback_query.message.answer("Пользователь не найден.")
            return

        # Логика для обработки выбранного времени
        selected_time = callback_query.data.split(":")[1]
        await callback_query.message.answer(f"Вы выбрали время: {selected_time}")
    except Exception as e:
        await callback_query.message.answer(f"Произошла ошибка: {e}")