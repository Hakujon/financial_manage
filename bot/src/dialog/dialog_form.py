from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import (
    Button, Row, Calendar
)
from aiogram_dialog.widgets.text import (
    Format, Const
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
