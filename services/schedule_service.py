from sqlalchemy import Column, Integer, ForeignKey
from services.google_calendar_service import create_event, delete_event
from db.crud import create_lunch_slot, get_user_by_telegram_id, get_user_by_id, get_all_lunch_slots, delete_lunch_slot
from db.database import SessionLocal
from db.models import User, LunchSlot
from datetime import datetime, timedelta


async def get_manager_slots(manager_id: int):
    try:
        all_slots = get_all_lunch_slots()
        today = datetime.now().date()
        manager_slots = [
            slot for slot in all_slots
            if slot.manager_id == manager_id and slot.date >= today
        ]
        return manager_slots
    except Exception as e:
        raise Exception(f"Ошибка при получении слотов менеджера: {e}")


async def add_lunch_slot(date: datetime.date, start_time: datetime.time, manager_id: int):
    """
    Создаёт новый слот для обеда и добавляет событие в Google Calendar.
    """
    try:
        print(f"Creating slot: Date={date}, Start Time={start_time}, Manager ID={manager_id}")  # Отладочный вывод

        # Создаём новый слот
        with SessionLocal() as session:
            slot = create_lunch_slot(date=date, start_time=start_time, manager_id=manager_id)
            print(f"Slot created successfully: {slot}")  # Отладочный вывод

            # Получаем данные менеджера
            manager = session.query(User).filter(User.id == manager_id).first()
            if not manager:
                raise ValueError(f"Пользователь с ID {manager_id} не найден.")
            if not manager.email:
                raise ValueError(f"У менеджера {manager.last_name} {manager.first_name} отсутствует email для интеграции с Google Calendar.")

            # Формируем данные для события
            summary = "Обед с сотрудниками"
            description = f"Слот для обеда с менеджером {manager.last_name} {manager.first_name}"
            start_time_iso = datetime.combine(date, start_time).isoformat()
            end_time_iso = (datetime.combine(date, start_time) + timedelta(hours=1)).isoformat()
            attendees = [manager.email]

            print(f"Creating Google Calendar event: Summary={summary}, Start={start_time_iso}, End={end_time_iso}, Attendees={attendees}")  # Отладочный вывод

            # Создаём событие в Google Calendar
            event_id = create_event(summary, description, start_time_iso, end_time_iso, attendees)
            print(f"Google Calendar event created successfully: Event ID={event_id}")  # Отладочный вывод

            # Сохраняем event_id в слот
            slot.event_id = event_id
            session.add(slot)  # Привязываем объект к сессии
            session.commit()

        return slot
    except ValueError as e:
        print(f"ValueError: {e}")  # Отладочный вывод
        raise ValueError(str(e))
    except Exception as e:
        print(f"Exception: {e}")  # Отладочный вывод
        raise Exception(f"Ошибка при создании слота: {e}")


async def get_slot_details(slot_id: int):
    """
    Возвращает детали слота по его ID.
    """
    try:
        all_slots = get_all_lunch_slots()
        slot = next((s for s in all_slots if s.id == slot_id), None)
        if not slot:
            raise ValueError("Слот не найден.")
        return slot
    except Exception as e:
        raise Exception(f"Ошибка при получении деталей слота: {e}")


async def remove_lunch_slot(slot_id: int):
    """
    Удаляет слот по его ID и удаляет событие из Google Calendar.
    """
    try:
        # Получаем детали слота
        all_slots = get_all_lunch_slots()
        slot = next((s for s in all_slots if s.id == slot_id), None)
        if not slot:
            raise ValueError("Слот не найден.")

        print(f"Slot details: {slot}, Event ID: {slot.event_id}")  # Отладочный вывод

        # Удаляем событие из Google Calendar
        if slot.event_id:
            print(f"Attempting to delete event with ID: {slot.event_id}")  # Отладочный вывод
            delete_event(slot.event_id)

        # Удаляем слот из базы данных
        delete_lunch_slot(slot_id)
        print(f"Slot with ID {slot_id} deleted successfully.")  # Отладочный вывод
        return True
    except Exception as e:
        print(f"Error while removing slot with ID {slot_id}: {e}")  # Отладочный вывод
        raise Exception(f"Ошибка при удалении слота: {e}")


def delete_user_by_telegram_id(telegram_id: int):
    try:
        with SessionLocal() as session:
            # Получаем пользователя
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                raise ValueError(f"Пользователь с Telegram ID {telegram_id} не найден.")

            # Удаляем связанные слоты
            session.query(LunchSlot).filter(LunchSlot.manager_id == user.id).delete()

            # Удаляем пользователя
            session.delete(user)
            session.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
        raise


manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)