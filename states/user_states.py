from aiogram.fsm.state import State, StatesGroup

class UserCreationStates(StatesGroup):
    waiting_for_telegram_id = State()
    waiting_for_full_name = State()
    waiting_for_phone_number = State()
    waiting_for_role = State()

class UserDeletionStates(StatesGroup):
    waiting_for_telegram_id = State()

class LunchSlotCreationStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()

class LunchBookingStates(StatesGroup):
    waiting_for_manager = State()  # Ожидание выбора менеджера
    waiting_for_slot = State()  # Ожидание выбора слота