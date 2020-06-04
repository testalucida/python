from tkinter import ttk, Tk
from tkinter import messagebox
from enum import IntEnum
from business import DataProvider
from verwalterview import VerwalterView, VerwalterDialog
from stammdatenview import StammdatenAction
from interfaces import XVerwalter

VerwalterModifiedAction = IntEnum('VerwalterModifiedAction', 'new modified')

class VerwalterController:
    def __init__(self, dp:DataProvider, parent:ttk.Frame):
        self._dataProvider:DataProvider = dp
        self._dlgParent = parent
        self._dlg = None
        self._modifyCallback = None

    def registerModifiedCallback(self, callback) -> None:
        # callback function to register must take 3 arguments:
        #  action:StammdatenAction, data:XVerwalter, data_before:XVerwalter
        self._modifyCallback = callback

    def createVerwalter(self):
        self._showDialog()

    def editVerwalter(self, verwalter_id:int):
        #get verwalter data:
        vdata:XVerwalter = self._dataProvider.getVerwalterData(verwalter_id)
        self._showDialog(vdata)

    def _showDialog(self, verwalterData:XVerwalter = None):
        self._dlg = VerwalterDialog(self._dlgParent)
        self._dlg.attributes('-topmost', True)
        #self._dlg.attributes('-topmost', False)
        view:VerwalterView = self._dlg.view
        if verwalterData:
            view.setData(verwalterData)
        view.setButtonState('disabled', 'normal')
        view.registerModifyCallback(self._onModified)
        view.registerActionCallback(self._onAction)

    def _onModified(self):
        self._dlg.view.setButtonState('normal', 'normal')

    def _onAction(self, action:StammdatenAction, data:XVerwalter, data_before:XVerwalter):
        if action == StammdatenAction.save_changes:
            msg:str = self._validate(data, data_before)
            if msg:
                messagebox.showwarning('Speichern nicht möglich', msg)
            else:
                action = VerwalterModifiedAction.new
                if data.verwalter_id < 0:
                    self._dataProvider.insertVerwalter(data)
                else:
                    self._dataProvider.updateVerwalter(data)
                    action = VerwalterModifiedAction.modified
                if self._modifyCallback:
                    self._modifyCallback(action, data, data_before)
        else: #cancel
            if self._dlg.view.isModified():
                if not messagebox.askyesno(
                        'Bestätigung', 'Daten wurden geändert. Wirklich abbrechen?'):
                    return

        self._dlg.destroy()

    def _validate(self, data_mod: XVerwalter, data_before:XVerwalter) -> str:
        if not data_mod.firma:
            return 'Name der Firma muss angegeben sein.'
        if data_before:
            if data_mod.firma == data_before.firma and \
                data_mod.strasse == data_before.strasse and \
                data_mod.plz == data_before.plz and \
                data_mod.ort == data_before.ort and \
                data_mod.telefon == data_before.telefon and \
                data_mod.email == data_before.telefon:
                return 'Keine Änderungen erkannt.'
        return ''

def test():
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    vc = VerwalterController(dp, root)
    vc.createVerwalter()

    root.mainloop()

if __name__ == '__main__':
    test()
