from aiogram.fsm.state import State, StatesGroup

class start(StatesGroup):
    name = State()
    age = State()
    number = State()

class AddTask(StatesGroup):
    waiting_for_task = State()
