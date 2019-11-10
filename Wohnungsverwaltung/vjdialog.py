from tkinter import Tk, Toplevel
from tkinter import ttk
from mywidgets import MyCombobox
import datehelper

class VjDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Veranlagungsjahr auswählen")
        self._callback = None
        self.bind('<Key>', self._onKeyHit)  # handle escape key
        self._cbo = None
        self._createGui()

    def _createGui(self):
        cbo = MyCombobox(self)
        cbo.setItems(datehelper.getLastYears(3))
        cbo.setIndex(1)
        cbo.grid(column=0, row=0, columnspan=2, sticky='nswe', padx=5, pady=5)
        self._cbo = cbo

        okBtn = ttk.Button(self, text='OK', command=self._onOk)
        okBtn.grid(column=0, row=1, sticky='nswe', padx=5, pady=5)

        cancelBtn = ttk.Button(self, text='Abbrechen', command=self._onCancel)
        cancelBtn.grid(column=1, row=1, sticky='nswe', padx=5, pady=5)

    def registerCallback(self, callback):
        self._callback = callback

    def _onOk(self):
        if self._callback:
            self._callback(self._cbo.getValue())

    def _onCancel(self):
        self.destroy()

    def _onKeyHit(self, evt):
        if evt.keycode == 9: #escape
            self._onCancel()

if __name__ == '__main__':
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    dlg = VjDialog(root)

    root.mainloop()
