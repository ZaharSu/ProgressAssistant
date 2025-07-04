from aiogram.fsm.state import StatesGroup, State


class AddHabitStates(StatesGroup):
    title = State()
    description = State()
    purpose = State()


class AddWorkoutStates(StatesGroup):
    title = State()
    category = State()
    description = State()


class LogWorkoutStates(StatesGroup):
    workout_title = State()
    duration_minutes = State()
    sets = State()
    reps_per_set = State()
