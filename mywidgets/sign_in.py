from tkinter import *
from tkinter import ttk
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
        self._teName.focus()
        MyLabel(frame, 'Password: ', 0, 1, "nw", None, 3, (3, 10))
        self._tePwd = TextEntry(frame, 1, 1, "nwe", 3, (3, 10))
        self._tePwd.config(show="*")


def test():
    def cb(ok_or_cancel:bool):
        print(ok_or_cancel)

    root = Tk()
    root.option_add('*Dialog.msg.font', 'Helvetica 11')

    dlg = SignInDialog(root)
    dlg.setOkCancelCallback(cb)

    root.mainloop()


if __name__ == '__main__':
    test()