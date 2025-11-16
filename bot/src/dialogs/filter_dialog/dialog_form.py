from datetime import date, datetime
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog.api.entities import ChatEvent
from aiogram_dialog import Window, DialogManager, Dialog
from aiogram_dialog.widgets.kbd import (
    Button, Row, Calendar, ManagedCalendar,
    Select, SwitchTo, Back, Cancel
)
from aiogram_dialog.widgets.text import (
    Format, Const
)
from src.service.service import (
    get_categories,
    create_filter,
    get_exp_by_filters
)
from src.service.utils import (
    get_start_of_week, get_end_of_week,
    get_start_of_month
)

from math import ceil

PAGE_SIZE = 5


class FilterSG(StatesGroup):
    first_state = State()
    calendar_start_state = State()
    calendar_end_state = State()
    category_state = State()
    expenses_state = State()


async def clicked_this_week_button(callback: CallbackQuery,
                                   button: Button,
                                   dialog_manager: DialogManager):
    start_of_week = get_start_of_week()
    print(start_of_week)
    dialog_manager.dialog_data["start_date"] = start_of_week
    dialog_manager.dialog_data["end_date"] = None


async def clicked_this_month_button(callback: CallbackQuery,
                                    button: Button,
                                    dialog_manager: DialogManager):
    start_of_month = get_start_of_month()
    print(start_of_month)
    dialog_manager.dialog_data["start_date"] = start_of_month
    dialog_manager.dialog_data["end_date"] = None


async def clicked_all_time_button(callback: CallbackQuery,
                                  button: Button,
                                  dialog_manager: DialogManager):
    dialog_manager.dialog_data["start_date"] = None
    dialog_manager.dialog_data["end_date"] = None


first_window = Window(
    Const("Выберите временной промежуток"),
    Row(SwitchTo(
        text=Const("За всё время"),
        id="all_time",
        on_click=clicked_all_time_button,
        state=FilterSG.category_state
    )),
    Row(
        SwitchTo(
            text=Const("За эту неделю"),
            id="this_week",
            on_click=clicked_this_week_button,
            state=FilterSG.category_state
        ),
        SwitchTo(
            text=Const("За этот месяц"),
            id="this_month",
            on_click=clicked_this_month_button,
            state=FilterSG.category_state,
        )
    ),
    Row(
        SwitchTo(
            text=Const("Выбрать начальную дату"),
            id="calendar_button",
            state=FilterSG.calendar_start_state,
        )
    ),
    state=FilterSG.first_state
)


async def selected_start_date(
        callback: ChatEvent,
        widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: date):
    date = selected_date.isoformat()
    dialog_manager.dialog_data["start_date"] = date
    await dialog_manager.switch_to(FilterSG.calendar_end_state)


calendar_start = Calendar(
    id="calendar_start",
    on_click=selected_start_date
)


calendar_start_window = Window(
    Const("Выберите начальную дату"),
    calendar_start,
    state=FilterSG.calendar_start_state
)


async def selected_end_date(
        callback: ChatEvent,
        widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: date):
    date = selected_date.isoformat()
    dialog_manager.dialog_data["end_date"] = date
    await dialog_manager.switch_to(FilterSG.category_state)


calendar_end = Calendar(
    id="calendar_end",
    on_click=selected_end_date
)


calendar_end_window = Window(
    Const("Выберите конечную дату"),
    calendar_end,
    state=FilterSG.calendar_end_state
)


async def clicked_category_button(
    callback: CallbackQuery,
    widget,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data["category"] = item_id

    start = dialog_manager.dialog_data.get("start_date")
    end = dialog_manager.dialog_data.get("end_date")

    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None
    category = None if item_id == "All" else item_id

    expense_filter = create_filter(
        start_date=start_dt,
        end_date=end_dt,
        category=category
    )

    try:
        expenses_from_api = await get_exp_by_filters(filter=expense_filter)
    except Exception:
        expenses_from_api = ["Ошибка при получении расходов"]

    expenses = expenses_from_api if isinstance(expenses_from_api, list) else [str(expenses_from_api)]
    dialog_manager.dialog_data["expenses"] = expenses
    dialog_manager.dialog_data["page"] = 1

    await dialog_manager.switch_to(FilterSG.expenses_state)


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
    state=FilterSG.category_state
)


async def expenses_getter(dialog_manager: DialogManager, **kwargs) -> dict:
    page = int(dialog_manager.dialog_data.get("page", 1))

    expenses_cached = dialog_manager.dialog_data.get("expenses")

    if expenses_cached is None:
        start = dialog_manager.dialog_data.get("start_date")
        end = dialog_manager.dialog_data.get("end_date")
        category = dialog_manager.dialog_data.get("category")

        if start:
            start = datetime.fromisoformat(start)
        if end:
            end = datetime.fromisoformat(end)

        expense_filter = create_filter(
            start_date=start,
            end_date=end,
            category=(None if category == "All" else category)
        )

        expenses_from_api = await get_exp_by_filters(filter=expense_filter)
        expenses = expenses_from_api if isinstance(expenses_from_api, list) else [str(expenses_from_api)]
        dialog_manager.dialog_data["expenses"] = expenses
        expenses_cached = expenses
    expenses_list = expenses_cached

    total = len(expenses_list)
    total_pages = max(1, ceil(total / PAGE_SIZE))
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    page_items = expenses_list[start_idx:end_idx]

    expenses_text = "\n\n".join(page_items) if page_items else "Нет расходов"

    return {
        "expenses_text": expenses_text,
        "page": page,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "page_str": f"{page}/{total_pages}",
    }


async def _change_page(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, delta: int):
    cur = int(dialog_manager.dialog_data.get("page", 1))
    cur += delta
    dialog_manager.dialog_data["page"] = cur
    await dialog_manager.switch_to(FilterSG.expenses_state)


async def prev_page(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await _change_page(callback, button, dialog_manager, -1)


async def next_page(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await _change_page(callback, button, dialog_manager, 1)

async def clear_dialog_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()


expenses_window = Window(
    Const("Расходы по заданным фильтрам:"),
    Format("{expenses_text}"),
    Row(
        Button(Const("◀ Назад"), id="prev_page", on_click=prev_page, when="has_prev"),
        Button(Format("{page_str}"), id="page_info"),
        Button(Const("Вперед ▶"), id="next_page", on_click=next_page, when="has_next"),
    ),
    Row(SwitchTo(
        text=Const("Изменить фильтры"),
        id="change_filters",
        state=FilterSG.first_state,
        on_click=clear_dialog_data,
    )),
    Row(Back(Const("Назад")), Cancel(Const("Выход"))),
    getter=expenses_getter,
    state=FilterSG.expenses_state
)


windows = (
    first_window,
    calendar_start_window,
    calendar_end_window,
    category_window,
    expenses_window,
)


filter_dialog = Dialog(
    *windows
)
