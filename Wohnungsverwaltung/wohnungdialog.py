from tkinter import *
from tkinter import ttk
from functools import partial
from typing import Dict, List, Text
from mywidgets import TextEntry, MyLabel, MyCombobox, ToolTip
from buttonfactory import ButtonFactory
from stammdatenview import WohnungLabelframe

class WohnungDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self._lfWohnung = None
        self._cboVermieter = None
        self._cboVerwalter = None
        self._btnNewVermieter = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._createUI()

    def _createUI(self):
        padx = pady = 5
        #lf = self._createWohnungLabelframe(padx, pady)
        lf = WohnungLabelframe(self)
        lf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._lfWohnung = lf
        f = self._createCombosFrame(padx, pady)
        f.grid(column=0, row=1, sticky='nswe', padx=padx, pady=pady)

    def _createCombosFrame(self, padx:int, pady:int) -> ttk.Frame:
        f = ttk.Frame(self)
        #f.columnconfigure(0, weight=1)
        MyLabel(f, 'Vermieter', column=0, row=0, sticky='nsw', padx=padx, pady=pady)
        cbo = MyCombobox(f)
        cbo.setItems(('Martin Kendel, Schellenberg', 'Gudrun Kendel, Schellenberg'))
        cbo.setReadonly(True)
        cbo.grid(column=1, row=0, sticky='nswe', padx=padx, pady=pady)
        self._cboVermieter = cbo
        btn = ButtonFactory.getNewButton(f, 'Neuen Vermieter anlegen', self._onNewVermieter )
        btn.grid(column=2, row=0, sticky='nswe', padx=padx, pady=pady)
        #self._btnNewVermieter = btn

        MyLabel(f, 'Verwalter', column=0, row=1, sticky='nsw', padx=padx, pady=pady)
        cbo = MyCombobox(f)
        cbo.setItems(('Hugo Baldrian, Nürnberg', 'Susanne Schleimich, Fürth'))
        cbo.setReadonly(True)
        cbo.grid(column=1, row=1, sticky='nswe', padx=padx, pady=pady)
        self._cboVerwalter = cbo

        return f

    def _onNewVermieter(self, arg):
        print('onNewVermieter')

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
