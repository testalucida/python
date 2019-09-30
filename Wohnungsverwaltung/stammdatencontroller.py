from typing import Dict, List
from business import DataProvider, DataError, ServiceException
from mywidgets import TextEntry
from actions import Action
from stammdatenview import StammdatenView, StammdatenAction
from interfaces import XWohnungDaten, XVerwalter, XVermieter, \
    XVermieterList, XVerwalterList
import datehelper

class StammdatenController:
    def __init__(self, dataProvider: DataProvider,
                 stammdatenView: StammdatenView):
        self._dataProvider = dataProvider
        self._view = stammdatenView
        self._whg_id = None
        self._vermieterDic: Dict[int, str] = {} #dictionary of all vermieter
        self._verwalterDic: Dict[int, str] = {} #dictionary of all verwalter

    def startWork(self) -> None:
        self._view.registerModifyCallback(self.onStammdatenModify)
        self._view.registerActionCallback(self.onStammdatenAction)

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadStammdaten()

    def clear(self) -> None:
        self._whg_id = None
        self._view.clear()

    def _loadStammdaten(self):
        #get minimalistic wohnung stammdaten
        xwhgdata: XWohnungDaten = self._dataProvider. \
            getWohnungMinStammdaten(self._whg_id)
        vermieter_id = xwhgdata.vermieter_id
        verwalter_id = xwhgdata.verwalter_id

        #create and set vermieter combo list:
        xvmlist: XVermieterList = self._dataProvider.getVermieterListe()
        for vm in xvmlist.getList():
            cboItem = ''.join((vm.name, ' ', vm.vorname, ', ', vm.ort))
            self._vermieterDic[vm.vermieter_id] = cboItem
            if vm.vermieter_id == vermieter_id:
                xwhgdata.vermieter = cboItem
        self._view.setVermieterList(list(self._vermieterDic.values()))

        #create and set verwalter combo list
        xvwlist: XVerwalterList = self._dataProvider.getVerwalterListe()
        for vw in xvwlist.getList():
            cboItem = ''.join((vw.firma, ' ', vw.ort))
            self._verwalterDic[vw.verwalter_id] = cboItem
            if vw.verwalter_id == verwalter_id:
                xwhgdata.verwalter = cboItem
        self._view.setVerwalterList(list(self._verwalterDic.values()))

        self._view.setData(xwhgdata)

    def onStammdatenModify(self):
        self._view.setButtonState('normal', 'normal')

    def onStammdatenAction(self, action:StammdatenAction,
                           xdata:XWohnungDaten, xdatacopy:XWohnungDaten):
        # take proper action depending on given StammdatenAction
        #print(action, xdata)
        if action == StammdatenAction.revert_changes:
            xdata = xdatacopy
            self._view.setData(xdata)
        else:
            switcher = {
                StammdatenAction.save_changes: self._handleSaveChanges,
                StammdatenAction.new_vermieter: self._handleNewVermieter
            }
            switcher.get(action)(xdata)
        # elif action == StammdatenAction.save_changes:
        #     pass
        # elif action == StammdatenAction.new_vermieter:
        #     pass
    def _handleSaveChanges(self, xdata:XWohnungDaten):
        print('save')

    def _handleNewVermieter(self, xdata:XWohnungDaten):
        pass

def test():
    from tkinter import  Tk
    from tkinter import ttk

    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    root = root = Tk()

    style = ttk.Style()
    style.theme_use('clam')

    tv = StammdatenView(root)
    tv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    ctrl = StammdatenController(dp, tv)
    ctrl.startWork()
    ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()