from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def build_categories_keyboard(categories: list[str]):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(
            text=category,
            callback_data=f"category:{category}")

    return builder


def build_date_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Этот месяц",
                   callback_data="this_month")
    builder.button(text="Эта неделя",
                   callback_data="this_week")
    builder.button(text="Выбрать дату",
                   callback_data="calendar")
    return builder


def build_pagination_keyboard(page: int,
                              page_size: int,
                              expenses: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if page > 0:
        builder.button(
            text="Назад",
            callback_data=f"expenses_page:{page-1}"
        )
    if ((1+page)*page_size) < len(expenses):
        builder.button(
            text="Вперед",
            callback_data=f"expenses_page:{page+1}"
        )
    return builder.as_markup()
