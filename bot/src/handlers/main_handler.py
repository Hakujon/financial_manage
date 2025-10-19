from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_dialog import DialogManager, StartMode
from src.dialogs.main_dialog.main_dialog import MainDialogSG


router = Router()

@router.message(CommandStart())
async def start_command_handler(message: Message, dialog_manager: DialogManager):
    await message.answer('Welcome to the Financial Management Bot!')
    await dialog_manager.start(
        state=MainDialogSG.main_state,
        mode=StartMode.RESET_STACK
    )
