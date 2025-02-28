from tkinter import Tk, ttk, Frame, Label, Scrollbar, Canvas, HORIZONTAL, Widget
from typing import List, Tuple
import tkinter.font as tkFont

COLOR_TABLEVIEW = "#ffaaff" #light pink
COLOR_TABLEHEADER = "#14aa2c"
COLOR_TABLEBODY = "#067baa"  #blue
COLOR_TABLECOLUMN = "#c200ae" #pink

class Scrollable(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background=COLOR_TABLEBODY)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.xsc = Scrollbar(self, orient=HORIZONTAL)
        self.xsc.grid(row=1, column=0, sticky='we')

        self.ysc = Scrollbar(self)
        self.ysc.grid(row=0, column=1, sticky='ns')

        c = Canvas(self, bg="#ff2f33", #karminrot
                         xscrollcommand=self.xsc.set,
                         yscrollcommand=self.ysc.set)
        c.rowconfigure(0, weight=1)
        c.columnconfigure(0, weight=1)
        c.grid(row=0, column=0, sticky='nswe', padx=0, pady=0)

        c.bind("<Configure>", self._onFrameConfigure)
        c.bind('<Enter>', self._bindToMousewheel)
        c.bind('<Leave>', self._unbindFromMousewheel)

        self.xsc.config(command=c.xview)
        self.ysc.config(command=c.yview)
        self.canvas = c

    def addWidget( self, position:Tuple, **options ) -> int:
        """
        :param widget: the object to add to this canvas
        see: http://effbot.org/tkinterbook/canvas.htm#Tkinter.Canvas.create_window-method
        :param position: Window position, given as two coordinates (in form of a tuple)
        :param options:
            anchor=  Where to place the widget relative to the given position. Default is CENTER.
            height= Window height. Default is to use the window’s requested height.
            state= Item state. One of NORMAL, DISABLED, or HIDDEN.
            tags=  A tag to attach to this item, or a tuple containing multiple tags.
            width= Window width. Default is to use the window’s requested width.
            window= Window object.
            also see https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/create_window.html
        :return: The item id.
        """
        return self.canvas.create_window(position, options)

    def addWidgetNW( self, widget:Widget, x:int, y:int, width:int, height:int ):
        return self.addWidget( (x,y), window=widget, width=width, height=height, anchor="nw" )

    def _onFrameConfigure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bindToMousewheel(self, event):
        self.canvas.bind_all("<Button-4>", self._onMousewheel)
        self.canvas.bind_all("<Button-5>", self._onMousewheel)

    def _unbindFromMousewheel(self, event):
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _onMousewheel(self, event):
        self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

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
class TableColumn(Frame):
    def __init__(self, parent, width=-1):
        Frame.__init__(self, parent, background=COLOR_TABLECOLUMN)
        self._hidden = False
        self.width = width

    def isHidden(self) -> bool:
        return self._hidden

######################################################
class TableBody(Scrollable):
    def __init__(self, parent):
        Scrollable.__init__(self, parent)
        self['background'] = COLOR_TABLEBODY
        self.columnList:List[TableColumn] = list()
        self.padx = 3
        self.bind( "<Configure>", self.onConfigure )
        self._initialized = False

    def addColumn(self, width:int = -1):
        x = 0
        l = len(self.columnList)
        if l > 0:
            tc = self.columnList[l - 1]
            x = tc.winfo_width() + self.padx

        newCol = TableColumn(self.canvas, width)
        self.addWidgetNW(newCol, x, 0, width, 50)
        self.columnList.append(newCol)

        #print("addColumn: winfo_width=", newCol.winfo_width(), ", width=", newCol['width'])

    def onConfigure( self, event ):
        print( "onConfigure - event: ", event )
        self.winfo_toplevel().update()
        n = len(self.columnList)
        tcW = round( event.width/n )
        x = 0
        for tc in self.columnList:
            tc.place(x=x, y=0, width=tcW, height=event.height)
            x += tcW + self.padx


class TableView(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background=COLOR_TABLEVIEW)
        self.padx = 3
        self.pady = 3
        self.tableHeader = TableHeader(self)
        h = self.tableHeader.h + self.tableHeader.padT + self.tableHeader.padB
        self.tableHeader.place(x=0, y=self.pady,
                               relwidth=1.0,
                               height=h)

        self.tableBody = TableBody(self)
        bodyY = h + 2*self.pady
        self.tableBody.place(x=0, y=bodyY,
                               relwidth=1.0,
                               relheight=0.856)

    def addColumn(self, header:str, width:int = -1):
        self.tableHeader.addHeader(header)
        self.tableBody.addColumn(width)

    def getTableHeader(self) -> TableHeader:
        return self.tableHeader
######################################################
class TableController:
    def __init__(self, tv:TableView):
        self._tv:TableView = tv
######################################################
def testScrollableFrame():
    root = Tk()
    root.geometry("300x280+300+300")
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    f = Frame(root, background="#ffffff")
    f.rowconfigure(1, weight=1)
    f.columnconfigure(0, weight=1)
    f.grid(row=0, column=0, sticky="nswe", padx=3, pady=3)
    ttk.Label(f, text="TableView Development").grid(row=0, column=0, sticky="nwe", padx=3, pady=3)

    body = TableBody(f)
    body.grid(row=1, column=0, sticky='nswe', padx=3, pady=3)

    for i in range(10):
        x = i*53 + 5
        f1 = Frame(body.canvas, background="#000000")
        #f1.place(x=x, y=5, width=50, height=50)
        #body.canvas.create_window((x, 5), window=f1, anchor="nw", width=50, height=50)
        #body.addWidget((x, 5), window=f1, anchor="nw", width=50, height=50)
        #body.addWidgetNW( f1, x, 5, 50, 50 )
        body.addColumn( 80 )

    root.mainloop()


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

def scroll_example():
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    container = ttk.Frame(root)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    for i in range(50):
        ttk.Label(scrollable_frame, text="Sample scrolling label").pack()

    container.pack()
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()



if __name__ == "__main__":
    testScrollableFrame()
    #scroll_example()