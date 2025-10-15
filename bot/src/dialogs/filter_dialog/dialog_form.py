from datetime import date
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import (
    Button, Row, Calendar, ManagedCalendar,
    Select
)
from aiogram_dialog.widgets.text import (
    Format, Const
)
from src.utils.utils import show_expenses
from src.service.service import (
    get_categories,
    create_filter,
    get_exp_by_filters
)


class FSMFillForm(StatesGroup):
    first_state = State()
    calendar_start_state = State()
    calendar_end_state = State()
    category_state = State()


async def clicked_time_button(callback: CallbackQuery,
                              button: Button,
                              dialog_manager: DialogManager):
    dialog_manager.dialog_data["start_date"] = callback.data
    await callback.answer()
    await dialog_manager.switch_to(FSMFillForm.category_state)


async def clicked_all_time_button(callback: CallbackQuery,
                                  button: Button,
                                  dialog_manager: DialogManager):
    dialog_manager.dialog_data.pop("start_date", None)
    await callback.answer()
    await dialog_manager.switch_to(FSMFillForm.category_state)


async def clicked_calendar_button(callback: CallbackQuery,
                                  button: Button,
                                  dialog_manager: DialogManager):
    await callback.answer()
    await dialog_manager.switch_to(FSMFillForm.calendar_start_state)


first_window = Window(
    Const("Выберите временной промежуток"),
    Row(Button(
        text=Const("За всё время"),
        id="all_time",
        on_click=clicked_all_time_button
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
    Row(
        Button(
            text=Const("Выбрать начальную дату"),
            id="calendar_button",
            on_click=clicked_calendar_button
        )
    ),
    state=FSMFillForm.first_state
)


async def selected_start_date(
        callback: ChatEvent,
        widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: date):
    date = selected_date.isoformat()
    dialog_manager.dialog_data["start_date"] = date
    await dialog_manager.switch_to(FSMFillForm.calendar_end_state)


calendar_start = Calendar(
    id="calendar_start",
    on_click=selected_start_date
)


calendar_start_window = Window(
    Const("Выберите начальную дату"),
    calendar_start,
    state=FSMFillForm.calendar_start_state
)


async def selected_end_date(
        callback: ChatEvent,
        widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: date):
    date = selected_date.isoformat()
    dialog_manager.dialog_data["end_date"] = date
    await dialog_manager.switch_to(FSMFillForm.category_state)


calendar_end = Calendar(
    id="calendar_end",
    on_click=selected_end_date
)


calendar_end_window = Window(
    Const("Выберите конечную дату"),
    calendar_end,
    state=FSMFillForm.calendar_end_state
)


async def clicked_category_button(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data["category"] = item_id
    category = dialog_manager.dialog_data.get("category", "All")
    start_date = dialog_manager.dialog_data.get("start_date")
    end_date = dialog_manager.dialog_data.get("end_date")
    filter = create_filter(
        start_date=start_date,
        end_date=end_date,
        category=category
    )
    expenses = await get_exp_by_filters(filter)
    await dialog_manager.done()
    await show_expenses(
        event=callback,
        expenses=expenses
    )


async def get_categories_dict(
    dialog_manager: DialogManager,
    **kwargs
) -> dict:
    categories = await get_categories()
    return {"categories": categories}


category_select = Select(
    id="categories_select",
    item_id_getter=lambda x: x,
    text=Format("{item}"),
    items="categories",
    on_click=clicked_category_button
)

category_window = Window(
    Const("Выберите категорию"),
    category_select,
    getter=get_categories_dict,
    state=FSMFillForm.category_state
)


windows = (
    first_window,
    calendar_start_window,
    calendar_end_window,
    category_window
)


filter_dialog = Dialog(
    *windows
)
