from db.database import SessionLocal
from db.models import User
from datetime import datetime

def create_admin():
    with SessionLocal() as session:
        admin = User(
            telegram_id=123456789,  # Замените на ваш Telegram ID
            full_name="Ваше ФИО",  # Укажите ваше имя
            phone_number="+1234567890",  # Укажите ваш номер телефона
            role="admin",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        session.add(admin)
        session.commit()
        print("Администратор успешно добавлен!")

if __name__ == "__main__":
    create_admin()