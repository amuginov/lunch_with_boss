from db.crud import create_user, get_all_users, delete_user_by_telegram_id

async def add_user(telegram_id: int, last_name: str, first_name: str, middle_name: str, phone_number: str, email: str, role: str):
    """
    Создает нового пользователя.
    """
    try:
        user = create_user(
            telegram_id=telegram_id,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            phone_number=phone_number,
            email=email,
            role=role
        )
        return user
    except Exception as e:
        raise Exception(f"Ошибка при добавлении пользователя: {e}")

async def list_all_users():
    """
    Возвращает список всех пользователей.
    """
    try:
        users = get_all_users()
        return users
    except Exception as e:
        raise Exception(f"Ошибка при получении списка пользователей: {e}")

async def remove_user(telegram_id: int):
    """
    Удаляет пользователя по Telegram ID.
    """
    try:
        delete_user_by_telegram_id(telegram_id)
        return True
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Ошибка при удалении пользователя: {e}")