from typing import Union
from aiogram.types import Message, CallbackQuery
from bot.inline_keyboards import build_pagination_keyboard


PAGE_SIZE = 6


def get_expenses_page(
        expenses: list,
        page: int
) -> str:
    start_exp = page * PAGE_SIZE
    end_exp = start_exp + PAGE_SIZE
    expenses = expenses[start_exp: end_exp]
    if not expenses:
        return "You have no expenses"
    return "\n".join(expenses)


async def show_expenses(event: Union[Message, CallbackQuery],
                        expenses: list[str],
                        page: int | None = None):
    if not page:
        page = 0
    text = get_expenses_page(expenses, page)
    markup = build_pagination_keyboard(page,
                                       PAGE_SIZE,
                                       expenses)
    if isinstance(event, Message):
        await event.answer(text=text,
                           reply_markup=markup)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text,
                                      reply_markup=markup)
        await event.answer()
