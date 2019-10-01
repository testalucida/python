from tkinter import ttk
from tkinter import messagebox
from business import DataProvider
from verwalterview import VerwalterView, VerwalterDialog
from stammdatenview import StammdatenAction
from interfaces import XVerwalter

class VerwalterController:
    def __init__(self, dp:DataProvider, parent:ttk.Frame):
        self._dataProvider:DataProvider = dp
        self._dlgParent = parent
        self._dlg = None

    def createVerwalter(self):
        print('VerwalterController.createVerwalter.')
        self._showDialog()

    def editVerwalter(self, verwalter_id:int):
        print('VerwalterController.editVerwalter. id=', verwalter_id)

    def _showDialog(self):
        self._dlg = VerwalterDialog(self._dlgParent)
        view = self._dlg.view
        view.setButtonState('disabled', 'normal')
        view.registerModifyCallback(self._onModified)
        view.registerActionCallback(self._onAction)

    def _onModified(self):
        self._dlg.view.setButtonState('normal', 'normal')

    def _onAction(self, action:StammdatenAction, data:XVerwalter, data_before:XVerwalter):
        print(action, data, data_before)
        if action == StammdatenAction.revert_changes:
            if self._dlg.view.isModified():
                if not messagebox.askyesno(
                        'Bestätigung', 'Daten wurden geändert. Wirklich abbrechen?'):
                    return
            self._dlg.destroy()