from tkinter import *
from tkinter import ttk
from collections import UserDict
from typing import Dict, List
from enum import IntEnum
from functools import partial
from copy import deepcopy

import sys
sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from mywidgets import TextEntry, FloatEntry, MyLabel, MyCombobox
    from interfaces import XWohnungDaten, XVermieter, XVerwalter
    from editablegroup import EditSaveFunctionBar, EditableGroupAction
    from mycalendar import DateEntry
    import datehelper
    from buttonfactory import ButtonFactory
except ImportError:
    print("couldn't import my widgets.")

StammdatenAction = \
    IntEnum('StammdatenAction',
            'save_changes revert_changes cancel new_vermieter edit_vermieter new_verwalter edit_verwalter')

class StammdatenView(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self._teStrasse = None
        self._tePlz = None
        self._teOrt = None
        self._teWhg_bez = None
        self._deAngeschafft_am = None
        self._teEinhwert_az = None
        self._cboVermieter = None
        self._cboVerwalter = None
        self._xwhgdatacopy = None
        self._btnSave = None
        self._btnCancel = None
        self._isModified = False
        self._modifyCallback = None
        self._actionCallback = None
        self._createUI()
        self._teStrasse.focus()

    def _createUI(self):
        padx = pady = 5
        self.columnconfigure(1, weight=1)

        MyLabel(self, 'Straße: ', 0, 0, 'nswe', 'e', padx, pady)
        self._teStrasse = TextEntry(self, 1, 0, 'nswe', padx, pady)
        self._teStrasse.setBackground('My.TEntry', 'lightyellow')
        self._teStrasse.setWidth(30)
        self._teStrasse.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'PLZ/Ort: ', 0, 1, 'nswe', 'e', padx, pady)
        f = ttk.Frame(self)
        f.columnconfigure(1, weight=1)
        self._tePlz = TextEntry(f, 0, 0, 'nsw', padx=(0, 3))
        self._tePlz['width'] = 6
        self._tePlz.setBackground('My.TEntry', 'lightyellow')
        self._tePlz.registerModifyCallback(self._onWohnungModified)

        self._teOrt = TextEntry(f, 1, 0, 'nswe')
        self._teOrt.setBackground('My.TEntry', 'lightyellow')
        self._teOrt.setWidth(30)
        self._teOrt.registerModifyCallback(self._onWohnungModified)
        f.grid(column=1, row=1, sticky='nswe', padx=padx, pady=pady)

        MyLabel(self, 'Whg.-Bez.: ', 0, 2, 'nswe', 'e', padx, pady)
        self._teWhg_bez = TextEntry(self, 1, 2, 'nswe', padx, pady)
        self._teWhg_bez.setBackground('My.TEntry', 'lightyellow')
        self._teWhg_bez.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'Angeschafft am: ', 0, 3, 'nswe', 'e', padx, pady)
        de = DateEntry(self)
        de.setUseCalendar(False)
        de['width'] = 10
        de.grid(column=1, row=3, sticky='nw', padx=padx, pady=pady)
        self._deAngeschafft_am = de
        self._deAngeschafft_am.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'Einhts.wert-Az: ', 0, 4, 'nswe', 'e', padx, pady)
        self._teEinhwert_az = TextEntry(self, 1, 4, 'nswe', padx, pady)
        #self._teEinhwert_az.grid(columnspan=2)
        self._teEinhwert_az.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'Vermieter:', column=0, row=5, sticky='nse', anchor='e', padx=padx, pady=pady)
        cbo = MyCombobox(self)
        cbo.setReadonly(True)
        cbo.registerModifyCallback(self._onWohnungModified)
        cbo.grid(column=1, row=5, sticky='we', padx=padx, pady=pady)
        self._cboVermieter = cbo

        btn = ButtonFactory.getNewButton(self, 'Neuen Vermieter anlegen', partial(self._onAction, StammdatenAction.new_vermieter))
        btn.grid(column=2, row=5, sticky='swe', padx=(0, 0), pady=pady)
        btnEdit = ButtonFactory.getEditButton(self, 'Vermieterdaten ändern', partial(self._onAction, StammdatenAction.edit_vermieter))
        btnEdit.grid(column=3, row=5, sticky='swe', padx=(0,0), pady=pady)

        MyLabel(self, 'Verwalter:', column=0, row=6, sticky='nse', padx=padx, pady=pady)
        cbo = MyCombobox(self)
        cbo.setReadonly(True)
        cbo.registerModifyCallback(self._onWohnungModified)
        cbo.grid(column=1, row=6, sticky='we', padx=padx, pady=pady)
        self._cboVerwalter = cbo

        btn2 = ButtonFactory.getNewButton(self, 'Neuen Verwalter anlegen',
                                          partial(self._onAction, StammdatenAction.new_verwalter))
        btn2.grid(column=2, row=6, sticky='swe', padx=(0,0), pady=pady)
        btnEdit2 = ButtonFactory.getEditButton(self, 'Verwalterdaten ändern',
                                               partial(self._onAction, StammdatenAction.edit_verwalter))
        btnEdit2.grid(column=3, row=6, sticky='swe', padx=(0, 0), pady=pady)

        f: ttk.Frame = self._createSaveCancelButtons()
        f.grid(column=1, columnspan=3, sticky='e', padx = padx, pady = pady)

    def _createSaveCancelButtons(self) -> ttk.Frame:
        f = ttk.Frame(self)
        btn = ttk.Button(f, text='Speichern', state='disabled',
                         command=partial(self._onAction, StammdatenAction.save_changes))
        btn.grid(column=0, row=0, sticky='nsw')
        self._btnSave = btn

        btn = ttk.Button(f, text='Verwerfen', state='disabled',
                         command=partial(self._onAction, StammdatenAction.revert_changes))
        btn.grid(column=1, row=0, sticky='nsw')
        self._btnCancel = btn
        return f

    def setButtonText(self, okbtntext:str, cancelbtntext:str) -> None:
        self._btnSave['text'] = okbtntext
        self._btnCancel['text'] = cancelbtntext

    def setButtonState(self, okbtnstate:str=None, cancelbtnstate:str=None) -> None:
        if okbtnstate:
            self._btnSave['state'] = okbtnstate
        if cancelbtnstate:
            self._btnCancel['state'] = cancelbtnstate

    def _onWohnungModified(self, widget: Widget, name: str, index: str, mode: str):
        self._isModified = True
        if self._modifyCallback:
            self._modifyCallback()

    def _onAction(self, action, arg=None):
        if self._actionCallback:
            self._actionCallback(action, self.getData(), self._xwhgdatacopy)
        if action == StammdatenAction.save_changes or \
                action == StammdatenAction.revert_changes:
            self._isModified = False

    def registerModifyCallback(self, callback) -> None:
        #function to register takes no arguments
        self._modifyCallback = callback

    def registerActionCallback(self, callback) -> None:
        #function to register has to take three arguments:
        #  - StammdatenAction
        #  - XWohnungDaten
        #  - XWohnungDaten (values before modifying)
        self._actionCallback = callback

    def isModified(self) -> bool:
        return self._isModified

    def setData(self, data: XWohnungDaten) -> None:
        self._teStrasse.setValue(data.strasse)
        self._tePlz.setValue(data.plz)
        self._teOrt.setValue(data.ort)
        self._teWhg_bez.setValue(data.whg_bez)
        self._deAngeschafft_am.setValue( data.angeschafft_am)
        self._teEinhwert_az.setValue(data.einhwert_az)
        self._cboVermieter.setValue(data.vermieter)
        self._cboVerwalter.setValue(data.verwalter)
        self._isModified = False
        self.setButtonState('disabled', 'disabled')
        self._xwhgdatacopy = deepcopy(data)

    def setVerwalterList(self, vwlist: List[str]):
        self._cboVerwalter.setItems(vwlist)

    def setVermieterList(self, vmlist: List[str]):
        self._cboVermieter.setItems(vmlist)

    def getData(self) -> XWohnungDaten:
        d: XWohnungDaten = XWohnungDaten()
        if self._xwhgdatacopy:
            # _xwhgdatacopy only exists in editing mode, not in new mode
            d.whg_id = self._xwhgdatacopy.whg_id
        d.strasse = self._teStrasse.getValue()
        d.plz = self._tePlz.getValue()
        d.ort = self._teOrt.getValue()
        d.whg_bez = self._teWhg_bez.getValue()
        d.angeschafft_am = self._deAngeschafft_am.getValue()
        d.einhwert_az = self._teEinhwert_az.getValue()
        d.verwalter = self._cboVerwalter.getValue()
        d.vermieter = self._cboVermieter.getValue()
        # d.verwalter_list = self._cboVerwalter.getItems()
        # d.vermieter_list = self._cboVermieter.getItems()
        return d

    def clear(self):
        self._teStrasse.clear()
        self._teWhg_bez.clear()
        self._tePlz.clear()
        self._teOrt.clear()
        self._teEinhwert_az.clear()
        self._deAngeschafft_am.clear()
        self._xwhgdatacopy = None

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    stv = StammdatenView(root)
    stv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    # ctrl = GrundsteuerController(dp, tv)
    # ctrl.startWork()
    # ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()
