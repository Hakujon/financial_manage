from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


def get_first_kb():
    kb_builder = ReplyKeyboardBuilder()
    create_plan_button = KeyboardButton(text="Создать план")
    show_expenses_button = KeyboardButton(text="Найти расходы")

    buttons = [create_plan_button,
               show_expenses_button]

    kb_builder.row(*buttons)
    return kb_builder.as_markup(resize_keyboard=True)
