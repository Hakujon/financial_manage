from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.reply_keyboard import head_keyboard
from bot.service import (
    get_categories,
    get_this_month_exp,
    get_category_exp,
    get_this_week_exp,
)
from bot.inline_keyboards import (
    build_categories_keyboard
)
from bot.utils import show_expenses


router = Router()


@router.message(F.text.startswith("Запись"))
async def create_note(message: Message):
    msg = message.text.split()
    await message.answer(str(len(msg)))
    if len(msg) in (3, 4):
        await message.answer("something not good")
    await message.answer(
        text="ВОТ твоя клавиатура",
        reply_markup=head_keyboard,
    )


@router.message(Command("expenses"))
async def show_keyboard(message: Message):
    await message.answer(
        text="Выберите расходы",
        reply_markup=head_keyboard
    )


@router.message(F.text == "Расходы эта неделя")
async def show_week_notes(message: Message):
    expenses = await get_this_week_exp()
    if isinstance(expenses, str):
        await message.answer(text=expenses)
        return True
    await message.answer(
        text="Вот твои записи за эту неделю")
    text = "\n\n".join(expenses)
    await message.answer(text=text)


@router.message(F.text == "Расходы этот месяц")
async def show_month_notes(message: Message):
    expenses_this_month = await get_this_month_exp()
    if not expenses_this_month:
        await message.answer(text="Not found")
        return True
    await message.answer(
        text="Вот твои записи за месяц:"
    )
    text = "\n\n".join(
        expense for expense in expenses_this_month)
    await message.answer(text=text)


@router.message(F.text == "Категории")
async def show_categories(message: Message):
    categories = await get_categories()
    keyboard = build_categories_keyboard(categories)
    await message.answer(
        text="tvoi kategorii:",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data.startswith("category:"))
async def show_category_notes(callback: CallbackQuery):
    category = callback.data.split(":", 1)[1]
    expenses = await get_category_exp(category)
    if not isinstance(expenses, list):
        text = expenses
    else:
        text = "\n\n".join(
            expense for expense in expenses
        )
    await callback.message.answer(text)


@router.callback_query(F.data.startswith("expenses_page:"))
async def paginate_expenses(callback: CallbackQuery, state: FSMContext):
    if callback.data:
        page = int(callback.data.split(":")[1])
    await show_expenses(callback, page, expenses)
