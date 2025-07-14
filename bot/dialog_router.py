from aiogram.types import Message
from aiogram_dialog import setup_dialogs
from aiogram_dialog import DialogManager, StartMode
from aiogram import Router, F
from bot.dialog_form import filter_dialog, FSMFillForm


router = Router()

router.include_router(filter_dialog)


@router.message(F.text == "Фильтр")
async def start_filter(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(FSMFillForm.main_state,
                               mode=StartMode.RESET_STACK)

setup_dialogs(router)
