from tkinter import *
from tkinter import ttk
from tkinter import messagebox

class DialogBase(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title("Dialog Base")
        self.bind('<Key>', self._onKeyHit) #handle escape key
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.clientArea:ttk.Frame = None
        self._callback = None
        self._validationcallback = None
        self._createGui()

    def _createGui(self):
        padx=pady=3
        frame = ttk.Frame(self)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(row=0, column=0, sticky='nswe')

        ca = ttk.Frame(frame)
        ca.rowconfigure(0, weight=1)
        ca.columnconfigure(0, weight=1)
        ca.grid(row=0, column=0, sticky='nswe')
        self.clientArea = ca

        buttonframe = ttk.Frame(frame)
        #buttonframe.columnconfigure(0, weight=1)
        buttonframe.grid(row=1, column=0, sticky='swe', padx=padx, pady=pady)
        self._createButtons(buttonframe)

    def _createButtons(self, parent:ttk.Frame):
        # create a frame containing OK and Cancel buttons
        okBtn = ttk.Button(parent, text='OK', command=self.onOk)
        okBtn.grid(column=0, row=0, sticky='sw', padx=3)

        cancelBtn = ttk.Button(parent, text='Cancel', command=self.onCancel)
        cancelBtn.grid(column=1, row=0, sticky='sw')

    def setOkCancelCallback(self, cbfunc) -> None:
        """
        set a callback function which is called when the user hits ok or cancel.
        the given cbfunc has to accept a bool argument.
        :param cbfunc: function to call on OK or Cancel
        :return: None
        """
        self._callback = cbfunc

    def setValidationCallback(self, cbfunc):
        """
        set a callback function which is called when the user hits ok.
        the given function takes no argument and has to return a string or None.
        If None is returned, the dialog will be closed.
        If a string is returned it will be treated as validation violation message
        and will be displayed.
        :param cbfunc:
        :return:
        """
        self._validationcallback = cbfunc

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))

    def getClientArea(self) -> ttk.Frame:
        return self.clientArea

    def onOk(self):
        if self._validationcallback:
            msg = self._validationcallback()
            if msg:
                messagebox.showerror("Eingabe unvollständig", msg)
                return

        if self._callback:
            self._callback(True)
        self.destroy()

    def onCancel(self):
        if self._callback:
            self._callback(False)
        self.destroy()

    def _onKeyHit(self, evt):
        if evt.keycode == 9:  # escape
            self.onCancel()


def test():
    def cb(ok_or_cancel:bool):
        print(ok_or_cancel)

    root = Tk()
    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    dlg = DialogBase(root)
    dlg.setOkCancelCallback(cb)

    root.mainloop()


if __name__ == '__main__':
    test()