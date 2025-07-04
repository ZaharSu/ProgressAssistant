from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date
from aiogram import Bot
from users.models import TelegramUser
from habits.models import Habits, HabitsLog, Workout, WorkoutLog
from asgiref.sync import sync_to_async


@sync_to_async
def get_unlog_habits():
    today = date.today()
    users_data = []
    for tg_user in TelegramUser.objects.exclude(linked_user=None):
        habits = Habits.objects.filter(user=tg_user.linked_user)
        unlog = []
        for habit in habits:
            if not HabitsLog.objects.filter(habit=habit, date=today).exists():
                unlog.append(habit.title)

        if unlog:
            users_data.append((tg_user.telegram_id, unlog))

    return users_data

@sync_to_async
def get_unlog_workouts():
    today = date.today()
    users_data = []
    for tg_user in TelegramUser.objects.exclude(linked_user=None):
        workouts = Workout.objects.filter(user=tg_user.linked_user)
        unlog = []
        for workout in workouts:
            last_log = WorkoutLog.objects.filter(workout=workout).order_by('-date').first()
            if not last_log or (date.today() - last_log.date).days > 2:
                unlog.append(workout.title)

        if unlog:
            users_data.append((tg_user.telegram_id, unlog))

    return users_data

async def send_habit_reminders(bot: Bot):
    users_data = await get_unlog_habits()
    for telegram_id, habits in users_data:
        habits_text = '\n'.join(f'- {habit}' for habit in habits)
        await bot.send_message(telegram_id, f'Напоминание! Сегодня не отмечались привычки:\n{habits_text}')


async def send_workout_reminders(bot: Bot):
    users_data = await get_unlog_workouts()
    for telegram_id, workouts in users_data:
        workouts_text = '\n'.join(f'- {workout}' for workout in workouts)
        await bot.send_message(telegram_id, f'Напоминание! У вас давно не было тренировок:\n{workouts_text}')