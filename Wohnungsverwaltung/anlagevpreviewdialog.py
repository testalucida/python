from tkinter import *
from tkinter import ttk
from functools import partial
from typing import Dict

class AnlageVPreviewDialog(Toplevel):
    def __init__(self, parent, data: Dict):
        Toplevel.__init__(self, parent)
        self._data: Dict = data

        self.title('Anlage V Vorschau')
        self._createUI()

    def _createUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        padx = pady = 5

        #lf = self._createWohnungLabelframe(padx, pady)
        #lf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)

    def close(self):
        self.destroy()

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))

def openDialog(root, frame):
    d = AnlageVPreviewDialog(frame, None)
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
