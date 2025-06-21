from db.crud import create_user, delete_user_by_telegram_id, get_user_by_telegram_id

async def approve_registration(user_data):
    """
    Регистрирует пользователя.
    """
    try:
        # Проверяем, существует ли пользователь с таким Telegram ID
        existing_user = get_user_by_telegram_id(user_data["telegram_id"])
        if existing_user:
            raise ValueError(f"Пользователь с Telegram ID {user_data['telegram_id']} уже существует.")

        create_user(
            telegram_id=user_data["telegram_id"],
            last_name=user_data["last_name"],
            first_name=user_data["first_name"],
            middle_name=user_data["middle_name"],
            phone_number=user_data["phone_number"],
            email=user_data["email"],
            role=user_data["role"]
        )
    except Exception as e:
        raise Exception(f"Ошибка при регистрации пользователя: {e}")

async def reject_registration(telegram_id):
    """
    Отклоняет заявку на регистрацию.
    """
    delete_user_by_telegram_id(telegram_id)