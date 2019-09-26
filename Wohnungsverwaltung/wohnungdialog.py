from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from functools import partial
from typing import Dict, List, Text
from mywidgets import TextEntry, MyLabel, MyCombobox, ToolTip
from buttonfactory import ButtonFactory
from interfaces import XWohnungDaten
from stammdatenview import WohnungFrame

class WohnungDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self._fWohnung = None
        self._cboVermieter = None
        self._cboVerwalter = None
        self._btnNewVermieter = None
        self._btnSave = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._createUI()

    def _createUI(self):
        padx = pady = 5

        lf = self._createWohnungLabelframe(padx, pady)
        lf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)

        f = self._createCombosFrame(padx, pady)
        f.grid(column=0, row=1, sticky='nswe', padx=padx, pady=pady)

        btn = ttk.Button(self, text='Speichern', state='disabled', command=self._onSave)
        btn.grid(column=0, row=2, sticky='nse', padx=padx, pady=pady)
        self._btnSave = btn

        btn = ttk.Button(self, text='Abbrechen', command=self._onCancel)
        btn.grid(column=1, row=2, sticky='nse', padx=padx, pady=pady)

    def _createWohnungLabelframe(self, padx:int, pady:int):
        lf = ttk.Labelframe(self, text='Wohnungsdaten')
        lf.columnconfigure(0, weight=1)
        wf = WohnungFrame(lf)
        wf.registerModifyCallback(self._onWohnungModified)
        wf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._fWohnung = wf

        return lf

    def _createCombosFrame(self, padx:int, pady:int) -> ttk.Frame:
        f = ttk.Frame(self)
        #f.columnconfigure(0, weight=1)
        MyLabel(f, 'Vermieter:', column=0, row=0, sticky='nsw', padx=padx, pady=pady)
        cbo = MyCombobox(f)
        cbo.setItems(('Martin Kendel, Schellenberg', 'Gudrun Kendel, Schellenberg'))
        cbo.setReadonly(True)
        cbo.grid(column=1, row=0, sticky='we', padx=padx, pady=pady)
        self._cboVermieter = cbo

        btn = ButtonFactory.getNewButton(f, 'Neuen Vermieter anlegen', self._onNewVermieter )
        btn.grid(column=2, row=0, sticky='swe', padx=padx, pady=pady)

        MyLabel(f, 'Verwalter:', column=0, row=1, sticky='nsw', padx=padx, pady=pady)
        cbo = MyCombobox(f)
        cbo.setItems(('Hugo Baldrian, Nürnberg', 'Susanne Schleimich, Fürth'))
        cbo.setReadonly(True)
        cbo.grid(column=1, row=1, sticky='we', padx=padx, pady=pady)
        self._cboVerwalter = cbo

        btn2 = ButtonFactory.getNewButton(f, 'Neuen Verwalter anlegen', self._onNewVerwalter)
        btn2.grid(column=2, row=1, sticky='swe', padx=padx, pady=pady)

        return f

    def _onWohnungModified(self):
        data:XWohnungDaten = self._fWohnung.getData()
        self._btnSave['state'] = 'normal'

    def _onNewVermieter(self, arg):
        print('onNewVermieter')

    def _onNewVerwalter(self, arg):
        print('onNewVerwalter')

    def _onSave(self):
        pass

    def _onCancel(self):
        if self._fWohnung.isModified():
            if not messagebox.askyesno(
                    'Bestätigung', 'Daten wurden geändert. Wirklich abbrechen?'):
                return
        self.destroy()

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))

def openDialog(root):
    d = WohnungDialog(root)
    rootx = root.winfo_x()
    rooty = root.winfo_y()
    d.setPosition(rootx, rooty + 30)

def test():
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    f = ttk.Frame(root)
    f.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)
    b = ttk.Button(f, text='Show Wohnungdialog', command=partial(openDialog, root))
    b.grid(column=0, row=0, sticky='nswe')

    root.mainloop()

if __name__ == '__main__':
    test()
