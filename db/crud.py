from .database import SessionLocal
from .models import User

def get_user(user_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.id == user_id).first()

def get_user_by_telegram_id(telegram_id: int):
    with SessionLocal() as session:
        return session.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(telegram_id: int, full_name: str, phone_number: str, role: str):
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