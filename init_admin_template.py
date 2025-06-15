from db.database import SessionLocal
from db.models import User

def create_admin():
    with SessionLocal() as session:
        admin = User(
            telegram_id=123456789,  # Замените на ваш Telegram ID
            full_name="Ваше ФИО",  # Укажите ваше имя
            phone_number="+1234567890",  # Укажите ваш номер телефона
            role="admin",
            email="admin@example.com"  # Укажите email администратора
        )
        session.add(admin)
        session.commit()
        print("Администратор успешно добавлен!")

if __name__ == "__main__":
    create_admin()