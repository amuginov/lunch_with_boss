from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import LunchBookingStates
from db.crud import get_all_users, get_all_lunch_slots
from db.database import SessionLocal  # Импортируем SessionLocal
from db.models import LunchSlot, User  # Импортируем LunchSlot и User
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import time, datetime  # Импортируем time и datetime
from keyboards.employee import generate_booking_keyboard, generate_slots_keyboard, employee_keyboard
from utils.common import WEEKDAY_SHORTCUTS, MONTH_SHORTCUTS, return_to_main_menu

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

    # Генерируем inline-клавиатуру с менеджерами
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=manager.full_name, callback_data=f"select_manager:{manager.id}")]
            for manager in managers
        ]
    )

    await message.answer("С кем Вы хотите забронировать обед?", reply_markup=keyboard)
    await state.set_state(LunchBookingStates.waiting_for_manager)


@router.callback_query(F.data.startswith("select_manager:"))
async def choose_manager(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора менеджера.
    """
    # Извлекаем ID менеджера из callback_data
    manager_id = int(callback.data.split(":")[1])
    await state.update_data(manager_id=manager_id)

    # Получаем список свободных слотов для выбранного менеджера
    all_slots = get_all_lunch_slots()
    today = datetime.now().date()
    available_slots = [
        slot for slot in all_slots
        if slot.manager_id == manager_id and not slot.is_booked and slot.date >= today
    ]

    if not available_slots:
        await callback.message.answer("Нет доступных слотов для бронирования.")
        await state.clear()
        return

    # Генерируем inline-клавиатуру с доступными слотами
    keyboard = generate_slots_keyboard(available_slots)

    await callback.message.answer("Выберите слот для бронирования:", reply_markup=keyboard)
    await state.set_state(LunchBookingStates.waiting_for_slot)


@router.callback_query(F.data.startswith("select_slot:"))
async def book_slot(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора слота.
    """
    slot_id = int(callback.data.split(":")[1])

    with SessionLocal() as session:
        try:
            slot = session.query(LunchSlot).filter(LunchSlot.id == slot_id, LunchSlot.is_booked == False).first()
            if not slot:
                await callback.message.answer("Слот не найден или уже забронирован.")
                await state.clear()
                return

            slot.is_booked = True
            slot.booked_by_user_id = int(callback.from_user.id)
            session.commit()
            await callback.message.answer(f"Вы успешно забронировали обед с менеджером на {slot.date} {slot.start_time}.")
        except Exception:
            await callback.message.answer("Произошла ошибка при бронировании. Попробуйте снова.")
        finally:
            await return_to_main_menu(callback.message, "employee", employee_keyboard())
            await state.clear()


@router.message(F.text == "📋 Мои бронирования")
async def view_bookings(message: Message):
    """
    Показать все бронирования пользователя в виде кнопок.
    """
    user_telegram_id = message.from_user.id

    with SessionLocal() as session:
        # Проверяем, что пользователь с ролью "user" существует
        user = session.query(User).filter(User.telegram_id == user_telegram_id, User.role == "user").first()
        if not user:
            await message.answer("У вас нет доступа к этому функционалу.")
            return

        # Получаем бронирования пользователя
        bookings = session.query(LunchSlot).filter(LunchSlot.booked_by_user_id == user.telegram_id).all()
        print(f"Найденные бронирования для пользователя {user.telegram_id}: {bookings}")

        for booking in bookings:
            print(f"Проверка бронирования ID={booking.id}: Менеджер={booking.manager}")
            if booking.manager:
                print(f"Менеджер: {booking.manager.full_name}")
            else:
                print(f"Ошибка: Поле 'manager' пустое для бронирования ID={booking.id}")

        if not bookings:
            await message.answer("У вас нет активных бронирований.")
            return

        # Генерируем клавиатуру с бронированиями
        keyboard = generate_booking_keyboard(bookings)
        await message.answer("Ваши бронирования:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("detail_booking:"))
async def booking_details(callback: CallbackQuery):
    """
    Отображение деталей бронирования.
    """
    booking_id = int(callback.data.split(":")[1])

    with SessionLocal() as session:
        booking = session.query(LunchSlot).filter(LunchSlot.id == booking_id).first()
        if not booking:
            await callback.message.answer("Бронирование не найдено.")
            return

        # Форматируем дату и время
        formatted_date = booking.date.strftime("%A, %d %B")
        formatted_time = booking.start_time.strftime("%H:%M")
        response = (
            f"Детали бронирования:\n"
            f"- День недели: {formatted_date}\n"
            f"- Время: {formatted_time}\n"
            f"- Менеджер: {booking.manager.full_name}"
        )
        await callback.message.answer(response)


@router.callback_query(F.data.startswith("delete_booking:"))
async def delete_booking(callback: CallbackQuery):
    """
    Удаление бронирования и освобождение слота.
    """
    booking_id = int(callback.data.split(":")[1])

    with SessionLocal() as session:
        booking = session.query(LunchSlot).filter(LunchSlot.id == booking_id).first()
        if not booking:
            await callback.message.answer("Бронирование не найдено.")
            return

        # Сбрасываем статус бронирования
        booking.is_booked = False
        booking.booked_by_user_id = None
        session.commit()

        await callback.message.answer("Бронирование успешно удалено. Слот снова доступен для бронирования.")