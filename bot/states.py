from aiogram.fsm.state import StatesGroup, State


class AddHabitStates(StatesGroup):
    title = State()
    description = State()
    purpose = State()