from enum import IntEnum
from wohnungdialog import WohnungDialog

WohnungDialogMode = IntEnum('WohnungDialogMode', 'new modify')

class WohnungDialogController:
    def __init__(self):
        self._dlg:WohnungDialog = None

    def startWork(self, parent, mode: WohnungDialogMode):
        self._dlg = WohnungDialog(parent)
        self._d
        if mode == WohnungDialogMode.modify:
            pass


