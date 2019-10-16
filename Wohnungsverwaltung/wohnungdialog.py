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
        self._stammdatenView = None

        self._createUI()

    def _createUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        padx = pady = 5

        lf = self._createWohnungLabelframe(padx, pady)
        lf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)

    def _createWohnungLabelframe(self, padx:int, pady:int):
        lf = ttk.Labelframe(self, text='Wohnungsdaten')
        lf.columnconfigure(0, weight=1)
        wf = StammdatenView(lf)
        wf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._stammdatenView = wf
        return lf

    def getView(self) -> StammdatenView:
        return self._stammdatenView

    # def _onSave(self):
    #     data: XWohnungDaten = self._fWohnung.getData()
    #     #todo: callback so controller will receive needed info

    def close(self):
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
