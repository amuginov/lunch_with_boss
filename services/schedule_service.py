from db.crud import create_lunch_slot, get_user_by_telegram_id, get_all_lunch_slots, delete_lunch_slot
from datetime import datetime


async def get_manager_slots(manager_id: int):
    """
    Возвращает список слотов для указанного менеджера.
    """
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
    Создаёт новый слот для обеда.
    """
    try:
        slot = create_lunch_slot(date=date, start_time=start_time, manager_id=manager_id)
        return slot
    except ValueError as e:
        raise ValueError(str(e))  # Пробрасываем ошибку дублирования
    except Exception as e:
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
    Удаляет слот по его ID.
    """
    try:
        delete_lunch_slot(slot_id)
        return True
    except Exception as e:
        raise Exception(f"Ошибка при удалении слота: {e}")