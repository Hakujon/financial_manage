from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

kb_builder = ReplyKeyboardBuilder()
show_expns_week_button = KeyboardButton(text="Расходы эта неделя")
show_expns_month_button = KeyboardButton(text="Расходы этот месяц")
show_category_button = KeyboardButton(text="Категории")
show_filter_button = KeyboardButton(text="Фильтр")

buttons: list[KeyboardButton] = [show_expns_week_button,
                                 show_expns_month_button,
                                 show_category_button,
                                 show_filter_button]


kb_builder.row(*buttons)
head_keyboard = kb_builder.as_markup(resize_keyboard=True)
