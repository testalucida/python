from tkinter import Tk, Toplevel
from tkinter import ttk
from typing import List, Dict
from mywidgets import MyCombobox, CheckableItemList, CheckableItemTableView
import datehelper

class AnlageVAuswahlDialog(Toplevel):
    def __init__(self, parent, whgList: CheckableItemList):
        Toplevel.__init__(self, parent)
        self._whgList = whgList
        self.title("Jahr und Wohnungen für Veranlagung auswählen")
        self._callback = None
        self.bind('<Key>', self._onKeyHit)  # handle escape key
        self._cbo = None
        self._itemTableView = None
        self._createGui(self._whgList)

    def _createGui(self, whgList: CheckableItemList):
        cbo = MyCombobox(self)
        cbo.setItems(datehelper.getLastYears(3))
        cbo.setIndex(1)
        cbo.setTextPadding('Vj.TCombobox', 5, 5, 0)
        cbo.setWidth(5)
        cbo.setFont('Helvetica 16 bold')
        cbo.setReadonly(True)

        cbo.grid(column=0, row=0, columnspan=2, padx=5, pady=5)
        self._cbo = cbo

        itemTable = CheckableItemTableView(self)
        itemTable.setCheckableItemList(whgList)
        itemTable.grid(column=0, row=1, columnspan=2, padx=5, pady=5)
        self._itemTableView = itemTable

        okBtn = ttk.Button(self, text='OK', command=self._onOk)
        okBtn.grid(column=0, row=2, sticky='nswe', padx=5, pady=5)

        cancelBtn = ttk.Button(self, text='Abbrechen', command=self._onCancel)
        cancelBtn.grid(column=1, row=2, sticky='nswe', padx=5, pady=5)

    def registerCallback(self, callback):
        self._callback = callback

    def _onOk(self):
        if self._callback:
            itemList = self._itemTableView.getCheckableItemList()
            self._callback(self._cbo.getValue(), itemList)

    def _onCancel(self):
        self.destroy()

    def _onKeyHit(self, evt):
        if evt.keycode == 9: #escape
            self._onCancel()

if __name__ == '__main__':
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    itemList = CheckableItemList()
    itemList.appendItem('Wohnung 1', 5, True)
    itemList.appendItem('Haus 88', 3, False)
    itemList.appendItem('Gostenhofer Geisterhaus, Mendelstr. 24', 6, True)

    dlg = AnlageVAuswahlDialog(root, itemList)

    root.mainloop()
