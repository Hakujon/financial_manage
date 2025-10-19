from aiogram import Router
from aiogram_dialog import setup_dialogs
from src.dialogs.filter_dialog.dialog_form import filter_dialog
from src.dialogs.main_dialog.main_dialog import main_dialog

router = Router()
router.include_router(main_dialog)
router.include_router(filter_dialog)

setup_dialogs(router)
