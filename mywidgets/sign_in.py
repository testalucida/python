from tkinter import *
#from tkinter import ttk
from typing import List
from dialogbase import DialogBase
from mywidgets import MyLabel, TextEntry

class SignInDialog(DialogBase):
    def __init__(self, parent):
        DialogBase.__init__(self, parent)
        self.title("Sign in")
        self.setValidationCallback(self.validate)
        self._teName = None
        self._tePwd = None
        self._createFields()
        self.resizable(False, False)
        self._tePwd.focus()

    def validate(self) -> str or None:
        if len(self._teName.getValue()) < 1:
            return "Bitte Namen eingeben."
        if len(self._tePwd.getValue()) < 1:
            return "Bitte Passwort eingeben."
        return None

    def _createFields(self):
        frame = self.clientArea
        MyLabel(frame, 'Name: ', 0, 0, "nw", None, 3, (10,3))
        self._teName = TextEntry(frame, 1, 0, "nwe", 3, (10,3))
        MyLabel(frame, 'Password: ', 0, 1, "nw", None, 3, (3, 10))
        self._tePwd = TextEntry(frame, 1, 1, "nwe", 3, (3, 10))
        self._tePwd.config(show="*")

    def setName(self, name:str) -> None:
        self._teName.setValue(name)

    def getNameAndPassword(self) -> List[str]:
        return (self._teName.getValue(), self._tePwd.getValue())

def test():
    from tkinter import messagebox

    def cb(ok_or_cancel:bool):
        print(ok_or_cancel)
        # rc = messagebox.askquestion( "bla", "shall I")
        # print(rc)

    root = Tk()
    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    dlg = SignInDialog(root)
    dlg.setOkCancelCallback(cb)
    dlg.lift()
    dlg.wait_window()

    print("dlg created. Entering mainloop")

    root.mainloop()


if __name__ == '__main__':
    test()