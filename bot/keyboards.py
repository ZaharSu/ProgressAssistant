from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Мои привычки'), KeyboardButton(text='Мои тренировки')],
              [KeyboardButton(text='Добавить привычку'), KeyboardButton(text='Добавить тренировку')]
    ],
    resize_keyboard=True
)

