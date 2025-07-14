from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog import Dialog, Window
from bot.reply_keyboard import head_keyboard
from bot.dao import (
    get_categories,
    get_exp_by_filters,
    get_this_month_exp,
    get_category_exp,
    get_this_week_exp,
    create_filter
)
from bot.utiils import (
    build_categories_keyboard, FSMFillForm,
    build_date_keyboard
)


router = Router()

calendar_dialog = Dialog(
    Window(
        Calendar(
            id="calendar"
        ),
        state=FSMFillForm.fill_date
    )
)


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


@router.message(F.text == "Расходы эта неделя")
async def show_week_notes(message: Message):
    expenses = await get_this_week_exp()
    if isinstance(expenses, str):
        await message.answer(text=expenses)
        return True
    await message.answer(
        text="Вот твои записи за эту неделю")
    text = "\n\n".join(expense for expense in expenses)
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


# @router.message(F.text == "Фильтр")
# async def start_filter(message: Message, state: FSMContext):
#     date_keyboard = build_date_keyboard()
#     await state.set_state(FSMFillForm.fill_date)
#     await message.answer(text="Выбери дату",
#                          reply_markup=date_keyboard.as_markup())


# @router.callback_query(F.data.in_(["this_week", "this_month"]),
#                        FSMFillForm.fill_date)
# async def add_date_to_filter(callback: CallbackQuery, state: FSMContext):
#     start_date = callback.data
#     await state.update_data(start_date=start_date)
#     categories = await get_categories()
#     category_keyboard = build_categories_keyboard(categories)
#     await state.set_state(FSMFillForm.fill_category)
#     await callback.message.answer(text="Выбери категорию",
#                                   reply_markup=category_keyboard.as_markup())


# @router.callback_query(F.data.in_(["calendar"]),
#                        FSMFillForm.fill_date)
# async def set_calendar(callback: CallbackQuery, state: FSMContext,
#                        dialog_manager: DialogManager):
#     await dialog_manager.start(FSMFillForm.fill_date)






# @router.callback_query(F.data.startswith("category:"), FSMFillForm.fill_category)
# async def add_category_to_filter(callback: CallbackQuery, state: FSMContext):
#     category = callback.data.split(":", 1)[1]
#     await state.update_data(category=category)
#     data = await state.get_data()
#     filter = create_filter(
#         start_date=data["start_date"],
#         category=data["category"]
#     )
#     expenses = await get_exp_by_filters(filter=filter)
#     if not isinstance(expenses, list):
#         text = expenses
#     else:
#         text = "\n\n".join(
#             expense for expense in expenses
#         )
#     await callback.message.answer(text)
