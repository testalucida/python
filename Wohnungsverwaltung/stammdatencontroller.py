from libs import *
import utils
from business import DataProvider, DataError, ServiceException
from vermietercontroller import VermieterController
from verwaltercontroller import VerwalterController, VerwalterModifiedAction
from mywidgets import TextEntry
from actions import Action
from stammdatenview import StammdatenView, StammdatenAction
from interfaces import XWohnungDaten, XVerwalter, XVermieter, \
    XVermieterList, XVerwalterList
import datehelper
print(utils.getScriptPath())
class StammdatenController:
    def __init__(self, dataProvider: DataProvider,
                 stammdatenView: StammdatenView):
        self._dataProvider = dataProvider
        self._view = stammdatenView
        self._whg_id = None
        self._vermieterDic: Dict[int, str] = {} #dictionary of all vermieter
        self._verwalterDic: Dict[int, str] = {} #dictionary of all verwalter
        self._actionCompletedCallbacks = list()
        self._xwohnungDataTmp = None

    def startWork(self) -> None:
        self._view.registerModifyCallback(self.onStammdatenModify)
        self._view.registerActionCallback(self.onStammdatenAction)
        self._view.setVermieterList(self._getVermieterList())
        self._view.setVerwalterList(self._getVerwalterList())

    def registerWohnungActionCompletedCallback(self, callback) -> None:
        """
        registers a method or function to be called when a wohnung
        has been created or modified.
        :param callback:  method/function to be called.
        Has to accept 2 arguments:
            - kind of action (StammdatenAction)
            - interface XWohnungDaten
        :return:
        """
        self._actionCompletedCallbacks.append(callback)

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

        self._getVermieterListAndSyncX(xwhgdata)
        self._getVerwalterListAndSyncX(xwhgdata)

        self._view.setData(xwhgdata)

    def _getVermieterListAndSyncX(self, xdata:XWohnungDaten):
        self._view.setVermieterList(self._getVermieterList())
        if xdata.vermieter_id > 0:
            xdata.vermieter = self._vermieterDic[xdata.vermieter_id]

    def _getVermieterList(self) -> List[str]:
        xvmlist: XVermieterList = self._dataProvider.getVermieterListe()
        for vm in xvmlist.getList():
            cboItem = ''.join((vm.name, ' ', vm.vorname, ', ', vm.ort))
            self._vermieterDic[vm.vermieter_id] = cboItem
        return list(self._vermieterDic.values())

    def _getVerwalterListAndSyncX(self, xdata:XWohnungDaten):
        self._view.setVerwalterList(self._getVerwalterList())
        if xdata.verwalter_id > 0:
            okstate, cancelstate = self._view.getButtonState()
            xdata.verwalter = self._verwalterDic[xdata.verwalter_id]
            self._view.setVerwalter(xdata.verwalter)
            self._view.setButtonState(okstate, cancelstate)

    def _getVerwalterList(self) -> List[str]:
        xvwlist: XVerwalterList = self._dataProvider.getVerwalterListe()
        for vw in xvwlist.getList():
            cboItem = ''.join((vw.firma, ' ', vw.ort))
            self._verwalterDic[vw.verwalter_id] = cboItem
        return list(self._verwalterDic.values())

    def onStammdatenModify(self):
        self._view.setButtonState('normal', 'normal')

    def onStammdatenAction(self, action:StammdatenAction,
                           xdata:XWohnungDaten, xdatacopy:XWohnungDaten) -> None:
        """
        called by actions of stammdatenview (save, undo changes, cancel,
        create or edit verwalter or vermieter)
        :param action: kind of action
        :param xdata: interface XWohnungDaten containing modified data
        :param xdatacopy: interface XWohnungDaten containing data before
        beeing changed resp. None if a new wohnung is created
        :return:  None
        """

        # xdata doesn't contain vermieter_id and verwalter_id, so we have
        #to provide them by using vermieter and verwalter:
        self._provideVermieterIdAndVerwalterId(xdata)

        # take proper action depending on given StammdatenAction
        if action == StammdatenAction.revert_changes:
            if self._view.isModified():
                if not messagebox.askyesno('Bestätigung', 'Änderungen verwerfen?'):
                    return
            if xdatacopy: # edit mode - show data before editing
                xdata = xdatacopy
                self._view.setData(xdata)
            else: # create mode, close view/dialog due to cancelling
                self._doActionCompletedCallback(StammdatenAction.cancel, xdata)
        elif action == StammdatenAction.save_changes:
            # save modified wohnung data
            xdata.whg_id = self._handleSaveChanges(xdata)
            self._view.setButtonState('disabled', 'disabled')
            self._view.setData(xdata)
            self._doActionCompletedCallback(action, xdata)
        else:
            if action == StammdatenAction.new_vermieter:
                self._createVermieter()
            elif action == StammdatenAction.edit_vermieter:
                self._xwohnungDataTmp = xdata
                self._editVermieter(xdata.vermieter)
            elif action == StammdatenAction.new_verwalter:
                self._createVerwalter()
            elif action == StammdatenAction.edit_verwalter:
                self._xwohnungDataTmp = xdata
                self._editVerwalter(xdata.verwalter)

            if action == StammdatenAction.new_vermieter or \
                    action == StammdatenAction.edit_vermieter:
                self._getVermieterListAndSyncX(xdata)
            # else:
            #     self._getVerwalterListAndSyncX(xdata)

    def onWohnungDatenChangedByOthers(self, angeschafft_am: str,
                                      einhwert_az: str) -> None:
        xdata: XWohnungDaten = self._view.getData()
        xdata.angeschafft_am = angeschafft_am
        xdata.einhwert_az = einhwert_az
        self._view.setData(xdata)

    def _handleSaveChanges(self, xdata:XWohnungDaten):
        whg_id = xdata.whg_id
        msg = self._validateWohnungData(xdata)
        if msg:
            messagebox.showerror('Daten unvollständig', msg)
            return whg_id

        self._provideVermieterIdAndVerwalterId(xdata)

        if xdata.whg_id < 0:
            # insert new wohnung
            whg_id = self._dataProvider.insertWohnungMin(xdata)
        else:
            # update existing wohnung
            whg_id = self._dataProvider.updateWohnungMin(xdata)

        return whg_id

    def _provideVermieterIdAndVerwalterId(self, xdata:XWohnungDaten):
        if xdata.vermieter:
            # get vermieter's id by name
            xdata.vermieter_id = \
                self._getIdByName(self._vermieterDic, xdata.vermieter)
        else:
            xdata.vermieter_id = -1

        if xdata.verwalter:
            # get verwalter's id by name
            xdata.verwalter_id = \
                self._getIdByName(self._verwalterDic, xdata.verwalter)
        else:
            xdata.verwalter_id = -1

    def _validateWohnungData(self, xdata:XWohnungDaten) -> str or None:
        if not xdata.strasse:
            return 'Straße muss angegeben sein.'
        if not xdata.plz:
            return 'PLZ muss angegeben sein.'
        if not xdata.ort:
            return 'Ort muss anngegeben sein.'
        if not xdata.whg_bez:
            return 'Wohnungsbezeichnung muss angegeben sein; ggf. "Gesamtes Objekt".'
        return None

    def _doActionCompletedCallback(self, action: StammdatenAction,
                                  xdata: XWohnungDaten):
        for cb in self._actionCompletedCallbacks:
            cb(action, xdata)

    def _getIdByName(self, dic, searchname):
        return \
            next((id for id, name in dic.items() if name == searchname), -1)

    def _createVermieter(self):
        verm_ctrl = VermieterController(self._dataProvider)
        # new vermieter
        verm_ctrl.createVermieter()

    def _editVermieter(self, vermieter:str = None):
        verm_ctrl = VermieterController(self._dataProvider)
        if not vermieter:
            messagebox.showerror('Aktion nicht möglich',
                                 'Es ist kein Vermieter ausgewählt.')
            return

        #edit vermieter
        #get vermieter_id by means of vermieter and call vermieter controller
        for id, name in self._vermieterDic.items():
            if name == vermieter:
                verm_ctrl.editVermieter(id)
                return

    def _createVerwalter(self):
        verw_ctrl = VerwalterController(self._dataProvider, self._view)
        # new verwalter
        verw_ctrl.createVerwalter()

    def _editVerwalter(self, verwalter: str):
        verw_ctrl = VerwalterController(self._dataProvider, self._view)
        verw_ctrl.registerModifiedCallback(self.onVerwalterModified)
        if not verwalter:
            messagebox.showerror('Aktion nicht möglich',
                                 'Es ist kein Verwalter ausgewählt.')
            return
        # edit verwalter
        # get vermieter_id by means of vermieter and call vermieter controller
        for id, firma in self._verwalterDic.items():
            if firma == verwalter:
                verw_ctrl.editVerwalter(id)
                return

    def onVerwalterModified(self, action:VerwalterModifiedAction,
                            data:XVerwalter, data_before:XVerwalter):
        self._getVerwalterListAndSyncX(self._xwohnungDataTmp)

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
    #ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()