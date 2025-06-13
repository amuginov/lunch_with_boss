from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import LunchBookingStates
from keyboards.employee import generate_booking_keyboard, generate_slots_keyboard, employee_keyboard
from utils.common import return_to_main_menu
from services.booking_service import (
    get_available_managers,
    get_available_slots,
    book_slot,
    get_user_bookings,
    delete_booking,
    get_booking_details,
)

router = Router()

@router.message(F.text == "🍽 Забронировать обед")
async def start_booking(message: Message, state: FSMContext):
    managers = await get_available_managers()

    if not managers:
        await message.answer("Нет доступных менеджеров для бронирования.")
        return

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
        # Получаем данные о бронировании
        slot_data = await book_slot(slot_id, callback.from_user.id)

        # Формируем сообщение об успешном бронировании
        await callback.message.answer(
            f"Вы успешно забронировали обед с менеджером {slot_data['manager_name']} "
            f"на {slot_data['date']} в {slot_data['start_time']}."
        )
    except ValueError as e:
        await callback.message.answer(str(e))
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при бронировании: {e}")
    finally:
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
        await delete_booking(booking_id)
        await callback.message.answer("Бронирование успешно удалено. Слот снова доступен для бронирования.")
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