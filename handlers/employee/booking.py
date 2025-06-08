from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user_states import LunchBookingStates
from db.crud import get_all_users, get_all_lunch_slots
from db.database import SessionLocal  # Импортируем SessionLocal
from db.models import LunchSlot, User  # Импортируем LunchSlot и User
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from datetime import time  # Импортируем time
from keyboards.employee import generate_booking_keyboard

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

    # Генерируем кнопки с менеджерам
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

    with SessionLocal() as session:
        try:
            # Получаем ID менеджера по имени
            manager = session.query(User).filter(User.full_name == slot_data["manager"]).first()
            if not manager:
                print(f"Менеджер с именем {slot_data['manager']} не найден.")
                await message.answer("Менеджер не найден.")
                await state.clear()
                return

            # Выводим данные для отладки
            print(f"Выбранный слот: {selected_slot}")
            print(f"Дата: {selected_slot.split()[0]}, Время: {selected_slot.split()[1]}")
            print(f"Типы данных: Дата={type(selected_slot.split()[0])}, Время={type(selected_slot.split()[1])}")

            # Преобразуем время в объект time
            selected_time = time.fromisoformat(selected_slot.split()[1])  # Преобразуем строку в объект времени

            # Фильтруем слот по дате, времени и ID менеджера
            slot = session.query(LunchSlot).filter(
                LunchSlot.date == selected_slot.split()[0],
                LunchSlot.start_time == selected_time,  # Используем объект времени
                LunchSlot.manager_id == manager.id,
                LunchSlot.is_booked == False  # Убедимся, что слот не забронирован
            ).first()

            if slot:
                print(f"Слот найден: ID={slot.id}, дата={slot.date}, время={slot.start_time}")
                # Обновляем слот
                slot.is_booked = True
                slot.booked_by_user_id = int(message.from_user.id)
                session.commit()
                print(f"Слот обновлён: ID={slot.id}, booked_by_user_id={slot.booked_by_user_id}")
                await message.answer(f"Вы успешно забронировали обед с менеджером {slot_data['manager']} на {selected_slot}.")
            else:
                print(f"Слот не найден или уже забронирован. Дата: {selected_slot.split()[0]}, Время: {selected_slot.split()[1]}, Менеджер ID: {manager.id}")
                await message.answer("Слот не найден или уже забронирован.")
        except Exception as e:
            print(f"Ошибка при бронировании: {e}")
            await message.answer("Произошла ошибка при бронировании. Попробуйте снова.")
        finally:
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
    Удаление бронирования.
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

        await callback.message.answer("Бронирование успешно удалено.")