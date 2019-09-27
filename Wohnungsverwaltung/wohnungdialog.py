from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from functools import partial
from typing import Dict, List, Text
from mywidgets import TextEntry, MyLabel, MyCombobox, ToolTip
from buttonfactory import ButtonFactory
from interfaces import XWohnungDaten
from stammdatenview import StammdatenView

class WohnungDialog(Toplevel):
    """
    opens StammdatenView as dialog
    """
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title('Wohnung anlegen')
        self._fWohnung = None
        self._cboVermieter = None
        self._cboVerwalter = None
        self._btnNewVermieter = None
        self._btnSave = None
        self._onSaveCallback = None

        self._createUI()

    def _createUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        padx = pady = 5

        lf = self._createWohnungLabelframe(padx, pady)
        lf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)

        f = self._createSaveCancelButtons()
        f.grid(column=0, row=2, sticky='nse', padx=padx, pady=pady)

    def _createWohnungLabelframe(self, padx:int, pady:int):
        lf = ttk.Labelframe(self, text='Wohnungsdaten')
        lf.columnconfigure(0, weight=1)
        wf = StammdatenView(lf)
        wf.registerModifyCallback(self._onWohnungModified)
        wf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._fWohnung = wf

        return lf

    def _createSaveCancelButtons(self) -> ttk.Frame:
        f = ttk.Frame(self)
        btn = ttk.Button(f, text='Speichern', state='disabled', command=self._onSave)
        btn.grid(column=0, row=0, sticky='nsw')
        self._btnSave = btn

        btn = ttk.Button(f, text='Abbrechen', command=self._onCancel)
        btn.grid(column=1, row=0, sticky='nsw')
        return f

    def _onWohnungModified(self):
        self._btnSave['state'] = 'normal'

    def _onNewVermieter(self, arg):
        print('onNewVermieter')

    def _onNewVerwalter(self, arg):
        print('onNewVerwalter')

    def _onSave(self):
        data: XWohnungDaten = self._fWohnung.getData()
        #todo: callback so controller will receive needed info

    def _onCancel(self):
        if self._fWohnung.isModified():
            if not messagebox.askyesno(
                    'Bestätigung', 'Daten wurden geändert. Wirklich abbrechen?'):
                return
        self.destroy()

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))



def openDialog(root, frame):
    d = WohnungDialog(frame)
    rootx = root.winfo_x()
    rooty = root.winfo_y()
    d.setPosition(rootx + 10, rooty + 50)
    d.grab_set()

def test():
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    f = ttk.Frame(root)
    f.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)
    b = ttk.Button(f, text='Show Wohnungdialog', command=partial(openDialog, root, f))
    b.grid(column=0, row=0, sticky='nswe')

    root.mainloop()

if __name__ == '__main__':
    test()
