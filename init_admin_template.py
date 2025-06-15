from db.database import SessionLocal
from db.models import User

def create_admin():
    with SessionLocal() as session:
        # Проверяем, существует ли администратор с указанным Telegram ID
        existing_admin = session.query(User).filter(User.telegram_id == 123456789).first()
        if existing_admin:
            print("Администратор с таким Telegram ID уже существует.")
            return

        admin = User(
            telegram_id=123456789,  # Замените на ваш Telegram ID
            last_name="Фамилия",  # Укажите вашу фамилию
            first_name="Имя",  # Укажите ваше имя
            middle_name="Отчество",  # Укажите ваше отчество
            phone_number="+1234567890",  # Укажите ваш номер телефона
            role="admin",
            email="admin@example.com"  # Укажите email администратора
        )
        session.add(admin)
        session.commit()
        print("Администратор успешно добавлен!")

if __name__ == "__main__":
    create_admin()