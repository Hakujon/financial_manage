from datetime import date
from aiogram_dialog import DialogManager, Window, Dialog
from aiogram_dialog.widgets.kbd import Button, Back, Calendar, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from bot.dao import (get_categories,
                     create_filter,
                     get_exp_by_filters)


class FSMFillForm(StatesGroup):
    main_state = State()
    calendar_state = State()
    category_state = State()


async def clicked_time_button(callback: CallbackQuery,
                              button: Button,
                              dialog_manager: DialogManager):
    dialog_manager.dialog_data["start_date"] = callback.data
    await callback.answer()
    await dialog_manager.switch_to(FSMFillForm.category_state)


async def clicked_calendar_button(callback: CallbackQuery,
                                  button: Button,
                                  dialog_manager: DialogManager):
    await callback.answer()
    await dialog_manager.switch_to(FSMFillForm.calendar_state)


main_window = Window(
    Format("Choose time interval"),
    Row(Button(
        text=Const("За всё время"),
        id="all_time",
        on_click=clicked_time_button
    )),
    Row(
        Button(
            text=Const("За эту неделю"),
            id="this_week",
            on_click=clicked_time_button
        ),
        Button(
            text=Const("За этот месяц"),
            id="this_month",
            on_click=clicked_time_button
        )
    ),
    Row(Button(
        text=Const("Выбрать начальную дату"),
        id="calendar_button",
        on_click=clicked_calendar_button
    )),
    state=FSMFillForm.main_state
)


async def selected_date(callback: CallbackQuery,
                        widget: Calendar,
                        dialog_manager: DialogManager,
                        selected_date: date):
    dialog_manager.dialog_data["start_date"] = selected_date
    await callback.answer()
    await dialog_manager.switch_to(FSMFillForm.category_state)


calendar = Calendar(
    id="calendar",
    on_click=selected_date
)


calendar_window = Window(
    Const("Календарь"),
    calendar,
    state=FSMFillForm.calendar_state
)


async def clicked_category_button(callback: CallbackQuery,
                                  button: Button,
                                  dialog_manager: DialogManager,
                                  ):
    dialog_manager.dialog_data["category"] = callback.data
    category = dialog_manager.dialog_data["category"]
    start_date = dialog_manager.dialog_data["start_date"]
    filter = create_filter(start_date=start_date,
                           category=category)
    expenses = await get_exp_by_filters(filter)
    if not isinstance(expenses, list):
        text = expenses
    else:
        text = "\n".join(expense for expense in expenses)


async def get_category_buttons() -> list[Button]:
    categories = await get_categories()
    category_buttons = [
        Button(
            text=category,
            id=f"{category}",
            on_click=clicked_category_button
        )
        for category in categories
    ]
    return category_buttons

category_window = Window(
    Const("Выбор категории"),
    category_buttons,
    state=FSMFillForm.category_state
)