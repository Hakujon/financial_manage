from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.text import Const




class MainDialogSG(StatesGroup):
    main_state = State()


main_window = Window(
    Const("Это основное состояние"),
    state=MainDialogSG.main_state
)


main_dialog = Dialog(
    main_window
)
