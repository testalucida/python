from enum import IntEnum
from wohnungdialog import WohnungDialog
from interfaces import XWohnungDaten
from wvframe import WohnungAction
from business import DataProvider
from interfaces import XVermieterList, XVerwalterList

class WohnungDialogController:
    def __init__(self, parent, dp:DataProvider,
                 action: WohnungAction, whg_id:int = None):
        self._dlg:WohnungDialog = None
        self._parent = parent
        self._dataProvider = dp
        self._action: WohnungAction = action
        self._whg_id = whg_id

    def startWork(self):
        xdata: XWohnungDaten = None
        vmlist:XVermieterList = self._dataProvider.getVermieterListe()
        vwlist:XVerwalterList = self._dataProvider.getVerwalterListe()
        if self._action == WohnungAction.edit:
            #todo: get wohnung data (not: wohnung detail data)
            pass
        elif self._action == WohnungAction.new:
            xdata = XWohnungDaten()

        self._dlg = WohnungDialog(self._parent)
        self._dlg.setData(xdata)
        self._dlg.setVermieterList(vmlist)
        self._dlg.setVerwalterList(vwlist)


