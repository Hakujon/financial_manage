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
    create_expense
)
from bot.inline_keyboards import (
    build_categories_keyboard
)
from bot.utils import show_expenses
from bot.filters import ExpenseFormatFilter


router = Router()


@router.message(Command("expenses"))
async def show_keyboard(message: Message):
    await message.answer(
        text="Выберите расходы",
        reply_markup=head_keyboard
    )


@router.message(F.text == "Расходы эта неделя")
async def show_week_notes(message: Message):
    expenses = await get_this_week_exp()
    await show_expenses(message, expenses)


@router.message(F.text == "Расходы этот месяц")
async def show_month_notes(message: Message):
    expenses_this_month = await get_this_month_exp()
    await show_expenses(message, expenses_this_month)


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
    await show_expenses(callback, expenses)


@router.callback_query(F.data.startswith("expenses_page:"))
async def get_new_page(callback: CallbackQuery,
                       state: FSMContext):
    data = await state.get_data()
    expenses = data.get("expenses", "pustenko")
    page = int(callback.data.split(":")[1])
    await show_expenses(callback,
                        expenses, page)


@router.message(ExpenseFormatFilter())
async def create_note(message: Message):
    msg = message.text
    try:
        await create_expense(msg)  # type: ignore
        await message.answer("Расход добавлен")
    except Exception as e:
        await message.answer(f"Произошла ошибочка: {e}")


@router.message()
async def answer_other_messages(message: Message):
    await message.answer(
        '''
        Ты можешь написать, чтобы записать расход:
        Число Категория <Описание>
        Категория Число <Описание>
        Или воспользоваться клавишами в меню, чтобы посмотреть расходы
        '''
    )
