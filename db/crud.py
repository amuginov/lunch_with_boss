from datetime import date, time, timedelta, datetime
from .database import SessionLocal
from .models import User, LunchSlot
from sqlalchemy.orm import joinedload

def get_user(user_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.id == user_id).first()

def get_user_by_telegram_id(telegram_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(telegram_id: int, full_name: str, phone_number: str, role: str):
    try:
        with SessionLocal() as session:
            user = User(
                telegram_id=telegram_id,
                full_name=full_name,
                phone_number=phone_number,
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
            # Рассчитываем время окончания (длительность слота 1 час)
            end_time = (datetime.combine(date, start_time) + timedelta(hours=1)).time()

            # Заменяем год на текущий
            current_year = datetime.now().year
            slot_date = date.replace(year=current_year)

            slot = LunchSlot(
                date=slot_date,
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