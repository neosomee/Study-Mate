from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
import aiosqlite
from app.db import Database
from app.classes import User
import app.keyboards as kb
import app.states as states
from app.classes import User, AddTask

db = Database(path="Study_bot.db")
router = Router()

class AddTaskState(StatesGroup):
    waiting_for_task = State()

class AddTask:
    def __init__(self, user_id, task):
        self.user_id = user_id
        self.task = task

async def get_tasks(user_id):
    async with aiosqlite.connect(db.path) as conn:
        tasks = await conn.execute(
            """
            SELECT * FROM tasks WHERE user_id = ?
            """,
            (user_id,)
        ).fetchall()
        return tasks

async def add_task(new_task):
    async with aiosqlite.connect(db.path) as conn:
        await conn.execute(
            """
            INSERT INTO tasks (user_id, task) VALUES (?, ?)
            """,
            (new_task.user_id, new_task.task)
        )
        await conn.commit()

@router.message(Command('start'))
async def start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user:
        return await message.answer(f'Привет, {user.fullname}', reply_markup=kb.markup)
    await state.set_state(states.start.name)
    await message.answer('Введите ваше фамилию и имя')


@router.message(F.text == 'Личный кабинет')
async def profile(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    await message.answer(
        f"""
Вас зовут {user.fullname}
Ваш возраст: {user.age}
Ваш номер: {user.number}
""",
        reply_markup=kb.profile
    )


# Starting
@router.callback_query(F.data == 'reregister')
async def reregister(call: CallbackQuery,  state: FSMContext):
    await state.set_state(states.start.name)
    await call.message.answer('Введите ваше фамилию и имя')


@router.message(states.start.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(states.start.age)
    await message.answer('Введите ваш возраст')


@router.message(states.start.age)
async def register_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введите корректный возраст")
    age = int(message.text)
    if age < 10 or age > 100:
        return await message.answer("Введите корректный возраст")
    await state.update_data(age=message.text)
    await state.set_state(states.start.number)
    await message.answer('Введите ваш номер телефона',reply_markup=kb.get_number)


@router.message(states.start.number, F.contact)
async def register_number(message: Message, state:FSMContext):
    await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()
    
    user = User(
        id=message.from_user.id,
        fullname=data["name"],
        age=data["age"],
        number=data["number"]
    )
    
    if await db.get_user(message.from_user.id):
        await db.edit_user(user)
    else:
        await db.save_user(user)
    
    await message.answer(f"""Информация успешно сохранена!
Ваше имя и фамилия: {data['name']}
Ваш возраст: {data['age']}
Номер: {data['number']}""", reply_markup=kb.markup)
    await state.clear()


# Команда "Личный кабинет"
@router.message(F.text == 'Личный кабинет')
async def personal_cabinet(message: Message):
    await message.answer("Это ваш личный кабинет.")

# Команда "Список задач"
@router.message(F.text == 'Список задач')
async def show_tasks_list(message: Message):
    user_id = message.from_user.id
    tasks = await db.get_tasks(user_id)

    if not tasks:
        await message.answer("У вас пока нет задач.", reply_markup=kb.markup)
        return

    tasks_str = "\n".join([f"{i + 1}. {task.task}" for i, task in enumerate(tasks)])
    await message.answer(f"Ваши задачи:\n{tasks_str}", reply_markup=kb.markup)

# Команда "Добавить задачу"
@router.message(F.text == 'Добавить задачу')
async def add_task_command(message: Message, state: FSMContext):
    await state.set_state(AddTaskState.waiting_for_task)
    await message.answer("Введите текст вашей задачи (можешь добавить время и дату) :")


# Обработка ввода задачи
@router.message(AddTaskState.waiting_for_task)
async def handle_task_input(message: Message, state: FSMContext):
    task_text = message.text.strip()

    if not task_text:
        await message.answer("Ваша задача не может быть пустой. Пожалуйста, введите текст задачи.")
        return

    user_id = message.from_user.id
    new_task = AddTask(user_id=user_id, task=task_text)
    await add_task(new_task)

    await state.clear()
    await message.answer("Задача успешно добавлена!", reply_markup=kb.markup)