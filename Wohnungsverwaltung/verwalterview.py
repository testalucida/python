from tkinter import *
from tkinter import ttk
from functools import partial
from copy import deepcopy

#import sys
#sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from mywidgets import TextEntry, FloatEntry, MyLabel, MyCombobox
    from interfaces import XVerwalter
    from buttonfactory import ButtonFactory
    from stammdatenview import StammdatenAction
except ImportError:
    print("couldn't import my widgets.")

class VerwalterView(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self._xverwaltercpy = None
        self._verwalter_id = -1
        self._teFirma = None
        self._teStrasse = None
        self._tePlz = None
        self._teOrt = None
        self._teTelefon = None
        self._teEmail = None
        self._btnSave = None
        self._btnCancel = None
        self._isModified = False
        self._modifyCallback = None
        self._actionCallback = None
        self._createUI()
        self._teFirma.focus()

    def _createUI(self):
        padx = pady = 5
        self.columnconfigure(1, weight=1)

        MyLabel(self, 'Firma: ', 0, 0, 'nswe', 'e', padx, pady)
        self._teFirma = TextEntry(self, 1, 0, 'nswe', padx, pady)
        self._teFirma.setBackground('My.TEntry', 'lightyellow')
        self._teFirma.registerModifyCallback(self._onVerwalterModified)

        MyLabel(self, 'Straße: ', 0, 1, 'nswe', 'e', padx, pady)
        self._teStrasse = TextEntry(self, 1, 1, 'nswe', padx, pady)
        self._teStrasse.setWidth(30)
        self._teStrasse.registerModifyCallback(self._onVerwalterModified)

        MyLabel(self, 'PLZ/Ort: ', 0, 2, 'nswe', 'e', padx, pady)
        f = ttk.Frame(self)
        f.columnconfigure(1, weight=1)
        self._tePlz = TextEntry(f, 0, 0, 'nsw', padx=(0, 3))
        self._tePlz['width'] = 6
        self._tePlz.registerModifyCallback(self._onVerwalterModified)

        self._teOrt = TextEntry(f, 1, 0, 'nswe')
        self._teOrt.setWidth(30)
        self._teOrt.registerModifyCallback(self._onVerwalterModified)
        f.grid(column=1, row=2, sticky='nswe', padx=padx, pady=pady)

        MyLabel(self, 'Telefon: ', 0, 3, 'nswe', 'e', padx, pady)
        self._teTelefon = TextEntry(self, 1, 3, 'nswe', padx, pady)
        self._teTelefon.registerModifyCallback(self._onVerwalterModified)

        MyLabel(self, 'Mail-Adresse: ', 0, 4, 'nswe', 'e', padx, pady)
        self._teEmail = TextEntry(self, 1, 4, 'nswe', padx, pady)
        self._teEmail.registerModifyCallback(self._onVerwalterModified)

        f:ttk.Frame = self._createSaveCancelButtons()
        f.grid(column=1, row=5, sticky='se', padx=padx, pady=pady)

    def _createSaveCancelButtons(self) -> ttk.Frame:
        f = ttk.Frame(self)
        btn = ttk.Button(f, text='Speichern', state='disabled',
                         command=partial(self._onAction, StammdatenAction.save_changes))
        btn.grid(column=0, row=0, sticky='nsw')
        self._btnSave = btn

        btn = ttk.Button(f, text='Abbrechen', state='disabled',
                         command=partial(self._onAction, StammdatenAction.revert_changes))
        btn.grid(column=1, row=0, sticky='nsw')
        self._btnCancel = btn
        return f

    def registerModifyCallback(self, callback) -> None:
        #function to register takes no arguments
        self._modifyCallback = callback

    def registerActionCallback(self, callback) -> None:
        #function to register has to take three arguments:
        #  - StammdatenAction
        #  - XVerwalter
        #  - XVerwalter (values before been modified)
        self._actionCallback = callback

    def isModified(self) -> bool:
        return self._isModified

    def setButtonState(self, okbtnstate:str, cancelbtnstate:str) -> None:
        self._btnSave['state'] = okbtnstate #one of 'normal', 'disabled'
        self._btnCancel['state'] = cancelbtnstate  # one of 'normal', 'disabled'

    def setData(self, data:XVerwalter) -> None:
        self._xverwaltercpy = deepcopy(data)
        self._verwalter_id = data.verwalter_id
        self._teFirma.setValue(data.firma)
        self._teStrasse.setValue(data.strasse)
        self._tePlz.setValue(data.plz)
        self._teOrt.setValue(data.ort)
        self._teTelefon.setValue(data.telefon)
        self._teEmail.setValue(data.email)
        self._isModified = False

    def getData(self) -> XVerwalter:
        xdata:XVerwalter = XVerwalter()
        xdata.verwalter_id = self._verwalter_id
        xdata.firma = self._teFirma.getValue()
        xdata.strasse = self._teStrasse.getValue()
        xdata.plz = self._tePlz.getValue()
        xdata.ort = self._teOrt.getValue()
        xdata.telefon = self._teTelefon.getValue()
        xdata.email = self._teEmail.getValue()
        return xdata

    def clear(self) -> None:
        self._xverwaltercpy = None
        self._verwalter_id = -1
        self._teFirma.clear()
        self._teStrasse.clear()
        self._tePlz.clear()
        self._teOrt.clear()
        self._teTelefon.clear()
        self._teEmail.clear()
        self._isModified = False

    def _onVerwalterModified(self, widget: Widget, name: str, index: str, mode: str) -> None:
        self._isModified = True
        if self._modifyCallback:
            self._modifyCallback()

    def _onAction(self, action, arg=None):
        if self._actionCallback:
            self._actionCallback(action, self.getData(), self._xverwaltercpy)
        if action == StammdatenAction.save_changes or \
                action == StammdatenAction.revert_changes:
            self._isModified = False

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class VerwalterDialog(Toplevel):
    """
    opens StammdatenView as dialog
    """
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title('Verwalter anlegen')
        self.view = self._createUI()
        #self.attributes('-topmost', True)  --> bad: message box will be not visible

    def _createUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        padx = pady = 5
        vv = VerwalterView(self)
        vv.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        return vv

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def openDialog(root, frame):
    d = VerwalterDialog(frame)
    rootx = root.winfo_x()
    rooty = root.winfo_y()
    d.setPosition(rootx + 10, rooty + 50)
    d.grab_set()

def testDialog():
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    f = ttk.Frame(root)
    f.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)
    b = ttk.Button(f, text='Show Verwalterdialog', command=partial(openDialog, root, f))
    b.grid(column=0, row=0, sticky='nswe')

    root.mainloop()


def test():
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    vv = VerwalterView(root)
    vv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    testDialog()
