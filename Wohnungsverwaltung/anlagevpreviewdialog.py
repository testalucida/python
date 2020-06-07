from tkinter import *
from tkinter import ttk
from functools import partial
from typing import Dict
from anlagevtableview import AnlageVTableView, AnlageVData

class AnlageVPreviewDialog(Toplevel):
    def __init__(self, parent, msg: str, data: AnlageVData):
        Toplevel.__init__(self, parent)
        self._msg: str = "" if msg is None else msg
        self._anlagev_tableview:AnlageVTableView = None
        self.title('Anlage V Simulation')
        self._createUI()
        if data:
            self._anlagev_tableview.setData(data)

    def _createUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        padx = pady = 5
        lf: ttk.Labelframe = self._createMessageFrame()
        lf.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        lf = self._createDataFrame()
        lf.grid(column=0, row=1, sticky='nswe', padx=padx, pady=pady)

    def _createMessageFrame(self) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text="Meldungen aus dem Anlage V Prozess")
        lf.columnconfigure(0, weight=1)
        txt = self._createTextWidget(lf)
        txt.insert(END, self._msg)
        return lf

    def _createDataFrame(self):
        lf = ttk.Labelframe(self, text="Anlage V Daten")
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)
        _anlagev_tableview = AnlageVTableView(lf)
        _anlagev_tableview.grid(row=0, column=0, sticky='nswe', padx=1, pady=1)
        return lf

    def _createTextWidget(self, parent: ttk.Labelframe):
        xscrollbar = Scrollbar(parent, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E + W)
        yscrollbar = Scrollbar(parent)
        yscrollbar.grid(row=0, column=1, sticky=N + S)
        txt = Text(parent, wrap=NONE, height=4,
                   xscrollcommand=xscrollbar.set,
                   yscrollcommand=yscrollbar.set)
        txt.grid(column=0, row=0, sticky='nswe', padx=5, pady=5)
        xscrollbar.config(command=txt.xview)
        yscrollbar.config(command=txt.yview)
        return txt

    def close(self):
        self.destroy()

    def setPosition(self, x: int, y: int) -> None:
        self.geometry("+%d+%d" % (x , y ))

def openDialog(root, frame):
    msg = "Zeile1\nZeile 2 ewig lang nichtssagend wie immer nur Unfug\n" \
          "Zeile3 zum Abschluss\n" \
          "Zeile4 schon fast nicht mehr zu sehen aber auch nicht schade drum um diesen Müll\n" \
          "Zeile5 muss gescrollt werden"
    d = AnlageVPreviewDialog(frame, msg, None)
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
