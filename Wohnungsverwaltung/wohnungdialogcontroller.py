from enum import IntEnum
from wohnungdialog import WohnungDialog
from interfaces import XWohnungDaten
from wvframe import WohnungAction

class WohnungDialogController:
    def __init__(self, parent, action: WohnungAction, whg_id:int = None):
        self._dlg:WohnungDialog = None
        self._parent = parent
        self._action: WohnungAction = action

    def startWork(self):
        xdata: XWohnungDaten = None
        #todo: get list of verwalter and list of vermieter
        if self._action == WohnungAction.edit:
            #todo: get wohnung data (not: wohnung detail data)
            pass
        self._dlg = WohnungDialog(self._parent)
        self._dlg.setData(xdata)


