from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, MessageInput, ManagedTextInput
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import (
    Row, Column, SwitchTo, Start
)
from aiogram.types import Message
from aiogram.enums import ContentType
from bot.src.dialogs.filter_dialog.dialog_form import FilterSG
from bot.src.schemas.schemas import CreatePlan
from bot.src.dialogs.main_dialog.filters import is_expense_format, is_plan_format
from bot.src.service.service import create_expense, create_plan



class MainDialogSG(StatesGroup):
    main_state = State()
    expenses_state = State()
    plans_state = State()


main_window = Window(
    Const("Это основное состояние"),
    Row(SwitchTo(
        Const("Перейти к расходам"),
        id="to_expenses",
        state=MainDialogSG.expenses_state
    ),
    SwitchTo(
        Const("Перейти к планам"),
        id="to_plans",
        state=MainDialogSG.plans_state
    ),
    Start(
        Const("Фильтр расходов"),
        id="filter_dialog",
        state=FilterSG.first_state
    )
    ),
    state=MainDialogSG.main_state
)


async def process_expense_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str
) -> None:
    expense_with_plan = await create_expense(text=text)
    await message.answer(expense_with_plan)


async def wrong_text_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError
) -> None:
    await message.answer("Неверный формат ввода. Пожалуйста, введите расход в формате 'сумма категория <описание>'.")


async def not_text_input(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager
) -> None:
    await message.answer("Пожалуйста, введите текстовое сообщение.")


expenses_window = Window(
    Const("Это состояние расходов"),
    TextInput(
        id="expense_input",
        type_factory=is_expense_format,
        on_success=process_expense_input,
        on_error=wrong_text_input,
    ),
    MessageInput(
        id="not_text_input",
        func=not_text_input,
        content_types=ContentType.ANY
    ),
    Row(
        SwitchTo(
            Const("Перейти к планам"),
            id="to_plans",
            state=MainDialogSG.plans_state
        ),
        SwitchTo(
            Const("Перейти к главному"),
            id="to_main",
            state=MainDialogSG.main_state
        ),
    ),
    state=MainDialogSG.expenses_state
)

async def process_plan_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        plan: CreatePlan
) -> None:
    plan_response = await create_plan(plan=plan)
    await message.answer(plan_response)


async def wrong_plan_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError
) -> None:
    await message.answer("Неверный формат ввода. Пожалуйста, введите план в формате 'категория сумма <дата начала>'.")


plans_window = Window(
    Const("Это состояние планов"),
    TextInput(
        id="plan_input",
        type_factory=is_plan_format,
        on_success=process_plan_input,
        on_error=wrong_plan_input,
    ),
    MessageInput(
        id="not_text_input",
        func=not_text_input,
        content_types=ContentType.ANY
    ),
    Row(
        SwitchTo(
            Const("Перейти к расходам"),
            id="to_expenses",
            state=MainDialogSG.expenses_state
        ),
        SwitchTo(
            Const("Перейти к главному"),
            id="to_main",
            state=MainDialogSG.main_state
        ),
    ),
    state=MainDialogSG.plans_state
)


main_dialog = Dialog(
    main_window,
    expenses_window
)
