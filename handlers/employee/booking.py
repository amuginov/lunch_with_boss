from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from states.user_states import LunchBookingStates
from keyboards.employee import generate_booking_keyboard, generate_slots_keyboard, employee_keyboard
from utils.common import return_to_main_menu, WEEKDAY_SHORTCUTS, MONTH_SHORTCUTS
from services.booking_service import (
    get_available_managers,
    get_available_slots,
    book_slot,
    get_user_bookings,
    delete_booking,
    get_booking_details,
)
from db.database import SessionLocal  # Исправленный импорт
from db.models import User

router = Router()

@router.message(F.text == "🍽 Забронировать обед")
async def start_booking(message: Message, state: FSMContext):
    managers = await get_available_managers()

    if not managers:
        await message.answer("Нет доступных менеджеров для бронирования.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{manager.last_name} {manager.first_name} {manager.middle_name or ''}".strip(),
                    callback_data=f"select_manager:{manager.id}"
                )
            ]
            for manager in managers
        ]
    )

    await message.answer("С кем Вы хотите забронировать обед?", reply_markup=keyboard)
    await state.set_state(LunchBookingStates.waiting_for_manager)


@router.callback_query(F.data.startswith("select_manager:"))
async def choose_manager(callback: CallbackQuery, state: FSMContext):
    manager_id = int(callback.data.split(":")[1])
    await state.update_data(manager_id=manager_id)

    available_slots = await get_available_slots(manager_id)

    if not available_slots:
        await callback.message.answer("Нет доступных слотов для бронирования.")
        await state.clear()
        return

    keyboard = generate_slots_keyboard(available_slots)
    await callback.message.answer("Выберите слот для бронирования:", reply_markup=keyboard)
    await state.set_state(LunchBookingStates.waiting_for_slot)


@router.callback_query(F.data.startswith("select_slot:"))
async def book_slot_handler(callback: CallbackQuery, state: FSMContext):
    slot_id = int(callback.data.split(":")[1])

    try:
        # Получаем данные пользователя из базы данных
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
            if not user or not user.email:
                raise ValueError("У пользователя отсутствует email. Обратитесь к администратору.")

        # Передаём e-mail пользователя в функцию бронирования
        slot_data = await book_slot(slot_id, user.id, user.email)

        # Формируем сообщение об успешном бронировании
        await callback.message.answer(
            f"Вы успешно забронировали обед с менеджером {slot_data['manager_name']} "
            f"на {slot_data['date']} в {slot_data['start_time']}."
        )

        # Отправляем уведомление менеджеру
        manager_telegram_id = slot_data["manager_telegram_id"]
        weekday = WEEKDAY_SHORTCUTS[slot_data["date"].strftime("%A").lower()]
        month = MONTH_SHORTCUTS[slot_data["date"].strftime("%m")]
        formatted_date = f"{weekday}, {slot_data['date'].day} {month}"
        formatted_time = slot_data["start_time"].strftime("%H:%M")

        await callback.bot.send_message(
            chat_id=manager_telegram_id,
            text=(
                f"{user.last_name} {user.first_name} {user.middle_name or ''} забронировал обед с Вами "
                f"на {formatted_date}, {formatted_time}."
            )
        )
    except ValueError as e:
        await callback.message.answer(str(e))
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при бронировании: {e}")
    finally:
        # Вызов функции return_to_main_menu
        await return_to_main_menu(callback.message, "employee", employee_keyboard())
        await state.clear()


@router.message(F.text == "📋 Мои бронирования")
async def view_bookings(message: Message):
    user_telegram_id = message.from_user.id

    try:
        # Получаем данные о бронированиях
        bookings = await get_user_bookings(user_telegram_id)

        if not bookings:
            await message.answer("У вас нет активных бронирований.")
            return

        # Генерируем клавиатуру с данными о бронированиях
        keyboard = generate_booking_keyboard(bookings)
        await message.answer("Ваши бронирования:", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Произошла ошибка при получении бронирований: {e}")


@router.callback_query(F.data.startswith("delete_booking:"))
async def delete_booking_handler(callback: CallbackQuery):
    booking_id = int(callback.data.split(":")[1])

    try:
        # Получаем данные пользователя из базы данных
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
            if not user or not user.email:
                raise ValueError("У пользователя отсутствует email. Обратитесь к администратору.")

        # Удаляем бронирование
        await delete_booking(booking_id, user.email)
        await callback.message.answer("Бронирование успешно удалено. Слот снова доступен для бронирования.")
        # Вызов функции return_to_main_menu
        await return_to_main_menu(callback.message, "employee", employee_keyboard())
    except ValueError as e:
        await callback.message.answer(str(e))
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при удалении бронирования: {e}")


@router.callback_query(F.data.startswith("detail_booking:"))
async def booking_details_handler(callback: CallbackQuery):
    booking_id = int(callback.data.split(":")[1])

    try:
        # Получаем детали бронирования
        booking_details = await get_booking_details(booking_id)

        # Формируем сообщение с деталями бронирования
        response = (
            f"Детали бронирования:\n"
            f"- Дата: {booking_details['date']}\n"
            f"- Время: {booking_details['start_time']} - {booking_details['end_time']}\n"
            f"- Менеджер: {booking_details['manager_name']}"
        )
        await callback.message.answer(response)
    except ValueError as e:
        await callback.message.answer(str(e))
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при получении деталей бронирования: {e}")