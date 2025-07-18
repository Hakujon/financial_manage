from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup


def build_categories_keyboard(categories: list[str]):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category,
            callback_data=f"category:{category}")

    return builder


class FSMFillForm(StatesGroup):
    fill_date = State()
    fill_category = State()


def build_date_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Этот месяц",
                   callback_data="this_month")
    builder.button(text="Эта неделя",
                   callback_data="this_week")
    builder.button(text="Выбрать дату",
                   callback_data="calendar")
    return builder
