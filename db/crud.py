from .database import SessionLocal
from .models import User

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