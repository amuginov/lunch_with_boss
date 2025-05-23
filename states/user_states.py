from aiogram.fsm.state import State, StatesGroup

class UserCreationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_phone_number = State()
    waiting_for_role = State()