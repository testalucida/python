from tkinter import Tk, ttk, Frame, Label
from typing import Dict, List, Any
import tkinter.font as tkFont

COLOR_TABLEVIEW = "#ffaaff" #light pink
COLOR_TABLEHEADER = "#14aa2c"
COLOR_TABLEBODY = "#067baa"  #blue
COLOR_TABLECOLUMN = "#c200ae" #pink

class TableHeader(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background=COLOR_TABLEHEADER)
        self.fontsize = 12
        self.fontstyle = tkFont.Font(family="Lucida Grande", size=self.fontsize)
        self.headers:List[Label] = list()
        self.h = 20
        self.padL = 3
        self.padR = 3
        self.padT = 3
        self.padB = 1
        self._maxX = 0

    def addHeader(self, text:str) -> int:
        l = Label(self, text=text, font=self.fontstyle)
        fontsize = self.fontstyle['size']
        x = self._maxX + self.padL
        w = 80
        h = self.h - self.padT - self.padB
        l.place(x=x, y=self.padT, width=w, height=h)
        self._maxX = x + w
        self.headers.append(l)
        return len(self.headers) - 1

    def getHeader(self, idx:int) -> Label:
        return self.headers[idx]

    def setHeaderWidth(self, idx:int, w:int):
        l = self.getHeader(idx)
        l.place(width=w)
######################################################
class TableColumn(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
######################################################
class TableView(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background=COLOR_TABLEVIEW)
        self.padx = 3
        self.pady = 3
        self.tableHeader = TableHeader(self)
        self.tableHeader.place(x=self.padx, y=self.pady,
                               relwidth=0.984,
                               height=self.tableHeader.h + self.tableHeader.padT + self.tableHeader.padB)

    def addColumn(self, header:str):
        self.tableHeader.addHeader(header)

    def getTableHeader(self) -> TableHeader:
        return self.tableHeader
######################################################
class TableController:
    def __init__(self, tv:TableView):
        self._tv:TableView = tv
######################################################

def test():
    root = Tk()
    root.geometry("300x280+300+300")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    f = Frame(root, background="#ffffff")
    f.rowconfigure(1, weight=1)
    f.columnconfigure(0, weight=1)
    f.grid(row=0, column=0, sticky="nswe", padx=3, pady=3)
    ttk.Label(f, text="TableView Development").grid(row=0, column=0, sticky="nwe", padx=3, pady=3)

    tv = TableView(f)
    tv.grid(row=1, column=0, sticky="nswe", padx=3, pady=3)
    tv.addColumn("Column 1")
    tv.addColumn("Column 2")

    
    root.mainloop()

if __name__ == "__main__":
    test()