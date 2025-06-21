from db.crud import get_all_users, get_all_lunch_slots
from db.database import SessionLocal
from db.models import LunchSlot, User
from datetime import datetime
from services.google_calendar_service import create_event, delete_event


async def get_available_managers():
    """
    Возвращает список менеджеров.
    """
    try:
        managers = [user for user in get_all_users() if user.role == "manager"]
        return managers
    except Exception as e:
        raise Exception(f"Ошибка при получении списка менеджеров: {e}")


async def get_available_slots(manager_id: int):
    """
    Возвращает список доступных слотов для указанного менеджера.
    """
    try:
        all_slots = get_all_lunch_slots()
        print(f"All slots before filtering: {all_slots}")  # Отладочный вывод
        today = datetime.now().date()
        available_slots = [
            slot for slot in all_slots
            if slot.manager_id == manager_id and not slot.is_booked and slot.date >= today
        ]
        print(f"Available slots for manager {manager_id}: {available_slots}")  # Отладочный вывод
        return available_slots
    except Exception as e:
        raise Exception(f"Ошибка при получении доступных слотов: {e}")


async def book_slot(slot_id: int, user_id: int, user_email: str):
    """
    Бронирует слот для пользователя и отправляет приглашение на e-mail.
    """
    with SessionLocal() as session:
        try:
            # Получаем слот
            slot = session.query(LunchSlot).filter(LunchSlot.id == slot_id, LunchSlot.is_booked == False).first()
            if not slot:
                raise ValueError("Слот не найден или уже забронирован.")

            # Проверяем e-mail пользователя
            if not user_email:
                raise ValueError("У пользователя отсутствует e-mail. Приглашение не может быть отправлено.")

            # Обновляем статус слота
            slot.is_booked = True
            slot.booked_by_user_id = user_id
            session.commit()

            # Формируем данные для Google Calendar
            summary = "Обед с менеджером"
            manager_name = f"{slot.manager.last_name} {slot.manager.first_name} {slot.manager.middle_name or ''}".strip()
            description = f"Бронирование обеда с менеджером {manager_name}"
            start_time_iso = datetime.combine(slot.date, slot.start_time).isoformat()
            end_time_iso = datetime.combine(slot.date, slot.end_time).isoformat()

            # Формируем список участников
            attendees = [user_email]
            if slot.manager.email:
                attendees.append(slot.manager.email)

            # Создаём событие в Google Calendar
            event_id = create_event(summary, description, start_time_iso, end_time_iso, attendees)
            slot.event_id = event_id
            session.commit()

            return {
                "date": slot.date,
                "start_time": slot.start_time,
                "manager_name": manager_name,
                "manager_telegram_id": slot.manager.telegram_id,  # Добавляем Telegram ID менеджера
                "event_id": event_id
            }
        except Exception as e:
            raise Exception(f"Ошибка при бронировании слота: {e}")


async def get_user_bookings(user_telegram_id: int):
    """
    Возвращает список бронирований пользователя.
    """
    with SessionLocal() as session:
        try:
            # Получаем пользователя по Telegram ID
            user = session.query(User).filter(User.telegram_id == user_telegram_id).first()
            if not user:
                raise ValueError("Пользователь не найден.")

            # Фильтруем слоты по booked_by_user_id
            bookings = session.query(LunchSlot).filter(LunchSlot.booked_by_user_id == user.id).all()

            # Извлекаем данные из объектов до закрытия сессии
            booking_data = [
                {
                    "id": booking.id,
                    "date": booking.date,
                    "start_time": booking.start_time,
                    "manager_name": (
                        f"{booking.manager.last_name} {booking.manager.first_name} {booking.manager.middle_name or ''}".strip()
                        if booking.manager else "Неизвестный менеджер"
                    ),
                }
                for booking in bookings
            ]
            return booking_data
        except Exception as e:
            raise Exception(f"Ошибка при получении бронирований пользователя: {e}")


async def delete_booking(booking_id: int, user_email: str):
    """
    Удаляет бронирование и событие из Google Calendar.
    """
    with SessionLocal() as session:
        try:
            booking = session.query(LunchSlot).filter(LunchSlot.id == booking_id).first()
            if not booking:
                raise ValueError("Бронирование не найдено.")

            print(f"Before deletion: {booking}")  # Отладочный вывод

            # Удаляем событие из Google Calendar
            if booking.event_id:
                delete_event(booking.event_id)

            # Освобождаем слот
            booking.is_booked = False
            booking.booked_by_user_id = None
            booking.event_id = None
            session.commit()

            print(f"After deletion: {booking}")  # Отладочный вывод
            return True
        except Exception as e:
            raise Exception(f"Ошибка при удалении бронирования: {e}")


async def get_booking_details(booking_id: int):
    """
    Возвращает детали бронирования по его ID.
    """
    with SessionLocal() as session:
        try:
            booking = session.query(LunchSlot).filter(LunchSlot.id == booking_id).first()
            if not booking:
                raise ValueError("Бронирование не найдено.")

            # Формируем имя менеджера
            manager_name = (
                f"{booking.manager.last_name} {booking.manager.first_name} {booking.manager.middle_name or ''}".strip()
                if booking.manager else "Неизвестный менеджер"
            )

            # Извлекаем данные о бронировании
            booking_details = {
                "id": booking.id,
                "date": booking.date,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "manager_name": manager_name,
            }
            return booking_details
        except Exception as e:
            raise Exception(f"Ошибка при получении деталей бронирования: {e}")