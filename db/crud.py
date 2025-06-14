from datetime import date, time, timedelta, datetime
from .database import SessionLocal
from .models import User, LunchSlot
from sqlalchemy.orm import joinedload

def get_user_by_telegram_id(telegram_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(telegram_id: int, last_name: str, first_name: str, middle_name: str, phone_number: str, email: str, role: str):
    try:
        with SessionLocal() as session:
            user = User(
                telegram_id=telegram_id,
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                phone_number=phone_number,
                email=email,
                role=role
            )
            session.add(user)
            session.commit()
            return user
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        raise

def get_all_users():
    with SessionLocal() as session:
        return session.query(User).all()

def delete_user_by_telegram_id(telegram_id: int):
    try:
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                raise ValueError(f"Пользователь с Telegram ID {telegram_id} не найден.")
            session.delete(user)
            session.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
        raise

def create_lunch_slot(date: date, start_time: time, manager_id: int):
    try:
        with SessionLocal() as session:
            # Проверяем, существует ли уже слот с такой же датой, временем и менеджером
            existing_slot = session.query(LunchSlot).filter(
                LunchSlot.date == date,
                LunchSlot.start_time == start_time,
                LunchSlot.manager_id == manager_id
            ).first()

            if existing_slot:
                raise ValueError("Слот с указанной датой и временем уже существует.")

            # Рассчитываем время окончания (длительность слота 1 час)
            end_time = (datetime.combine(date, start_time) + timedelta(hours=1)).time()

            # Создаём новый слот
            slot = LunchSlot(
                date=date,
                start_time=start_time,
                end_time=end_time,
                capacity=1,
                manager_id=manager_id,
                is_booked=False  # Новый слот всегда свободен
            )
            session.add(slot)
            session.commit()
            return slot
    except Exception as e:
        print(f"Ошибка при создании слота: {e}")
        raise

def delete_lunch_slot(slot_id: int):
    try:
        with SessionLocal() as session:
            slot = session.query(LunchSlot).filter(LunchSlot.id == slot_id).first()
            if not slot:
                raise ValueError(f"Слот с ID {slot_id} не найден.")
            session.delete(slot)
            session.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении слота: {e}")
        raise

def get_all_lunch_slots():
    """
    Получить все слоты обедов из базы данных с предварительной загрузкой менеджеров.
    """
    try:
        with SessionLocal() as session:
            return session.query(LunchSlot).options(joinedload(LunchSlot.manager)).all()
    except Exception as e:
        print(f"Ошибка при получении слотов: {e}")
        raise

def delete_booking(booking_id: int):
    try:
        with SessionLocal() as session:
            booking = session.query(LunchSlot).filter(LunchSlot.id == booking_id).first()
            if not booking:
                raise ValueError(f"Бронирование с ID {booking_id} не найдено.")
            booking.is_booked = False
            booking.booked_by_user_id = None
            session.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении бронирования: {e}")
        raise