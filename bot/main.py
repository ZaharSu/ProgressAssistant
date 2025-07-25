import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from asgiref.sync import sync_to_async
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import main_keyboard
from dotenv import load_dotenv
from uuid import uuid4
from datetime import date
from states import AddHabitStates, AddWorkoutStates, LogWorkoutStates
from sheduler import send_habit_reminders, send_workout_reminders
from  apscheduler.schedulers.asyncio import AsyncIOScheduler


import django
from config import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from users.models import TelegramUser
from habits.models import Habits, HabitsLog, Workout, WorkoutCategory, WorkoutLog

import logging

load_dotenv()
storage = MemoryStorage()
bot = Bot(os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s] %(message)s', level=logging.INFO)



@sync_to_async
def get_or_create_telegram_user(telegram_id, username, first_name, last_name):
    user_obj, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'token': str(uuid4())
        }
    )
    if not user_obj.token:
        user_obj.token = str(uuid4())
        user_obj.save()

    return user_obj, created

@sync_to_async
def is_user_linked(user_obj):
    return bool(user_obj.linked_user)

@sync_to_async
def create_habit(telegram_id, title, description, purpose):
    tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
    if tg_user.linked_user:
        Habits.objects.create(
            user=tg_user.linked_user,
            title=title,
            description=description,
            purpose=purpose
        )

@sync_to_async
def create_workout(telegram_id, title, category_title, description):
    tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
    category, created = WorkoutCategory.objects.get_or_create(user=tg_user.linked_user, title=category_title)
    if tg_user.linked_user:
        Workout.objects.create(
            user=tg_user.linked_user,
            title=title,
            category=category,
            description=description,
        )

@sync_to_async
def get_user_habits(telegram_id):
    try:
        tg_user = TelegramUser.objects.select_related('linked_user').get(telegram_id=telegram_id)
        user = tg_user.linked_user
        if not user:
            return None
        return list(Habits.objects.filter(user=user))
    except TelegramUser.DoesNotExist:
        return None

@sync_to_async
def get_habit_by_id(habit_id):
    return Habits.objects.filter(id=habit_id).first()

@sync_to_async
def is_habit_log(habit):
    return HabitsLog.objects.filter(habit=habit, date=date.today()).exists()

@sync_to_async
def get_habits_log(habit):
    return HabitsLog.objects.filter(habit=habit).count()

@sync_to_async
def habit_create_log(telegram_id, habit_title):
    tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
    habit = Habits.objects.get(user=tg_user.linked_user, title=habit_title)
    if tg_user.linked_user:
        HabitsLog.objects.create(
            user=tg_user.linked_user,
            habit=habit,
            date = date.today(),
            is_completed = True
        )

@sync_to_async
def get_workout_category_by_id(telegram_id):
    try:
        tg_user = TelegramUser.objects.select_related('linked_user').get(telegram_id=telegram_id)
        user = tg_user.linked_user
        if not user:
            return None
        return list(WorkoutCategory.objects.filter(user=user))
    except TelegramUser.DoesNotExist:
        return None

@sync_to_async
def get_workout_by_category_id(telegram_id, category_id):
    tg_user = TelegramUser.objects.select_related('linked_user').get(telegram_id=telegram_id)
    user = tg_user.linked_user
    return list(Workout.objects.filter(user=user, category_id=category_id))

@sync_to_async
def get_workout_by_id(telegram_id, workout_id):
    tg_user = TelegramUser.objects.select_related('linked_user').get(telegram_id=telegram_id)
    user = tg_user.linked_user
    return Workout.objects.filter(user=user, id=workout_id).first()

@sync_to_async
def get_workout_log_by_workout(workout):
    return WorkoutLog.objects.filter(workout=workout).last()

@sync_to_async
def get_workout_log_count(workout):
    return WorkoutLog.objects.filter(workout=workout).count()

@sync_to_async
def get_workout_log_count_today(workout):
    return WorkoutLog.objects.filter(workout=workout, date=date.today()).count()

@sync_to_async
def create_log_workout(telegram_id, workout_title, duration_minutes, sets, reps_per_set):
    tg_user = TelegramUser.objects.get(telegram_id=telegram_id)
    workout = Workout.objects.get(user=tg_user.linked_user, title=workout_title)
    if tg_user.linked_user:
        WorkoutLog.objects.create(
            workout = workout,
            date = date.today(),
            duration_minutes = duration_minutes,
            sets = sets,
            reps_per_set = reps_per_set
        )

@dp.message(CommandStart())
async def welcome(message:Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    user_obj, created = await get_or_create_telegram_user(telegram_id, username, first_name, last_name)
    if created:
        logging.info(f'Новый пользователь Telegram записан: {telegram_id}')
    else:
        logging.info(f'Пользователь уже есть: {telegram_id}')

    is_linked = await is_user_linked(user_obj)

    if is_linked:
        await message.answer(f'Привет, {first_name or 'друг'}!', reply_markup=main_keyboard)
    else:
        link = f"http://127.0.0.1:8000/telegram/connect/?token={user_obj.token}"
        await message.answer(f'Добро пожаловать!\nЧтобы пользоваться ботом, необходимо сначала связать его с аккаунтом сайта.\n'
                         f'Перейдите по ссылке, чтобы связать аккаунт:\n{link}')

@dp.message(F.text == 'Добавить привычку')
async def start_add_habit(message:Message, state: FSMContext):
    await message.answer('Введите название привычки:')
    await state.set_state(AddHabitStates.title)

@dp.message(AddHabitStates.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Введите описание привычки (или введите "-" если не нужно):')
    await state.set_state(AddHabitStates.description)

@dp.message(AddHabitStates.description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Введите цель (дней):')
    await state.set_state(AddHabitStates.purpose)

@dp.message(AddHabitStates.purpose)
async def get_purpose(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        title = data.get('title')
        description = data.get('description') if data.get('description') != '-' else ''
        purpose = int(message.text)

        telegram_id = message.from_user.id

        await create_habit(telegram_id, title, description, purpose)
        await message.answer(f'Привычка <b>{title}</b> успешно добавлена!', parse_mode='HTML')
        await state.clear()
    except ValueError:
        await message.answer('Проверьте правильность введенных данных!')

@dp.message(F.text == 'Добавить тренировку')
async def start_add_workout(message:Message, state: FSMContext):
    await message.answer('Введите название тренировки:')
    await state.set_state(AddWorkoutStates.title)

@dp.message(AddWorkoutStates.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer('Введите название категории:')
    await state.set_state(AddWorkoutStates.category)

@dp.message(AddWorkoutStates.category)
async def get_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer('Введите описание тренировки (или введите "-" если не нужно):')
    await state.set_state(AddWorkoutStates.description)

@dp.message(AddWorkoutStates.description)
async def get_description(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data.get('title')
    category = data.get('category')
    description = message.text if message.text != '-' else ''

    telegram_id = message.from_user.id

    await create_workout(telegram_id, title, category, description)
    await message.answer(f'Тренировка <b>{title}</b> успешно добавлена!', parse_mode='HTML')
    await state.clear()

@dp.message(F.text == 'Мои привычки')
async def habits_handler(message:Message):
    telegram_id = message.from_user.id
    habits = await get_user_habits(telegram_id)
    if not habits:
        await message.answer(f'У вас пока нет привычек')
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=habit.title, callback_data=f'habit_{habit.id}')] for habit in
                         habits])

    await message.answer(f'Вот привычки которые вы соблюдаете:', reply_markup=keyboard)


@dp.message(F.text == 'Мои тренировки')
async def works_handler(message:Message):
    telegram_id = message.from_user.id
    workouts_category = await get_workout_category_by_id(telegram_id)
    if not workouts_category:
        await message.answer(f'У вас пока нет категорий и тренировок')
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=category.title, callback_data=f'workout_category_{category.id}')] for category in
                         workouts_category])

    await message.answer(f'Выберите категорию:', reply_markup=keyboard)

@dp.callback_query(F.data.startswith('habit_'))
async def habit_detail(callback: CallbackQuery):
    habit_id = callback.data.split('_')[1]
    habit = await get_habit_by_id(habit_id)
    is_log = await is_habit_log(habit)
    habit_log_count = await get_habits_log(habit)

    if not habit:
        await callback.message.answer('Не удалось найти привычку.')
        return
    if is_log:
        info = (f'<b>{habit.title}</b>\n'
                f'{habit.description or 'Без описания.'}\n'
                f'Цель: {habit.purpose} дней\n'
                f'Вы соблюдаете привычку: {habit_log_count} день\n'
                f'Эта привычка сегодня отмечалась!')
        await callback.message.answer(info, parse_mode='HTML')
    else:
        info = (f'<b>{habit.title}</b>\n'
                f'{habit.description or 'Без описания.'}\n'
                f'Цель: {habit.purpose} дней\n'
                f'Вы соблюдаете привычку: {habit_log_count} день\n'
                f'Сегодня привычка не отмечалась!')
        log_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Отметить привычку', callback_data=f'log_habit_{habit.title}')]]
        )
        await callback.message.answer(info, parse_mode='HTML', reply_markup=log_keyboard)

@dp.callback_query(F.data.startswith('log_habit_'))
async def habit_log(callback: CallbackQuery):
    habit_title = callback.data.split('_')[-1]
    try:
        await habit_create_log(callback.from_user.id, habit_title)
        await callback.message.answer('Привычка отмечена!')
    except django.db.utils.IntegrityError:
        await callback.message.answer('Сегодня привычка отмечалась!')

@dp.callback_query(F.data.startswith('workout_category_'))
async def workout_category(callback: CallbackQuery):
    category_id = callback.data.split('_')[-1]
    workouts = await get_workout_by_category_id(callback.from_user.id, category_id)

    if not workouts:
        await callback.message.answer('Не удалось найти тренировки!')
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=workout.title, callback_data=f'workout_{workout.id}')]
                         for workout in
                         workouts])
    await callback.message.answer(f'Выберите тренировку:', reply_markup=keyboard)


@dp.callback_query(F.data.startswith('workout_'))
async def workout_category(callback: CallbackQuery):
    workout_id = callback.data.split('_')[1]
    workout = await get_workout_by_id(callback.from_user.id, workout_id)
    workout_log = await get_workout_log_by_workout(workout)
    workout_log_count = await get_workout_log_count(workout)
    workout_log_count_today = await get_workout_log_count_today(workout)

    if not workout:
        await callback.message.answer('Не удалось найти тренировку!')
        return

    log_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отметить тренировку', callback_data=f'log_workout_{workout.title}')]]
    )

    if workout_log:
        info = (f'<b>{workout.title}</b>\n'
                f'{workout.description or 'Без описания.'}\n'
                f'Время последней тренировки: {workout_log.duration_minutes or '-'} минут\n'
                f'Количество подходов: {workout_log.sets or '-'}\n'
                f'Количество повторений: {workout_log.reps_per_set or '-'}\n'
                f'С {workout.created_at.strftime('%d.%m.%Y')} у вас было {workout_log_count} тренировок\n'
                f'Сегодня у вас было {workout_log_count_today} тренировок!')
        await callback.message.answer(info, parse_mode='HTML', reply_markup=log_keyboard)
    else:
        info = (f'У вас еще не было занятий по этой тренировке')
        await callback.message.answer(info, parse_mode='HTML', reply_markup=log_keyboard)

@dp.callback_query(F.data.startswith('log_workout_'))
async def start_log_workout(callback: CallbackQuery, state: FSMContext):
    await state.update_data(workout_title=callback.data.split('_')[-1])
    await callback.message.answer('Введите время тренировки (минут):')
    await state.set_state(LogWorkoutStates.duration_minutes)

@dp.message(LogWorkoutStates.duration_minutes)
async def get_log_duration_minutes(message: Message, state: FSMContext):
    await state.update_data(duration_minutes=message.text)
    await message.answer('Введите количество подходов (или введите "-" если не нужно):')
    await state.set_state(LogWorkoutStates.sets)

@dp.message(LogWorkoutStates.sets)
async def get_log_sets(message: Message, state: FSMContext):
    await state.update_data(sets=message.text)
    await message.answer('Введите количество повторений в подходе (или введите "-" если не нужно):')
    await state.set_state(LogWorkoutStates.reps_per_set)

@dp.message(LogWorkoutStates.reps_per_set)
async def get_log_sets(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        workout_title = data.get('workout_title')
        duration_minutes = data.get('duration_minutes') if data.get('duration_minutes') != '-' else ''
        sets = data.get('sets') if data.get('sets') != '-' else ''
        reps_per_set = message.text if message.text != '-' else ''

        telegram_id = message.from_user.id

        await create_log_workout(telegram_id, workout_title, duration_minutes, sets, reps_per_set)
        await message.answer(f'Выполнение тренировки отмечено!', parse_mode='HTML')
        await state.clear()
    except ValueError:
        await message.answer('Проверьте правильность введенных данных!')

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_habit_reminders, 'cron', hour=18, minute=0, args=[bot])
    scheduler.add_job(send_workout_reminders, 'cron', hour=18, minute=0, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())