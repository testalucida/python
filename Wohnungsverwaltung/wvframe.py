from tkinter import *
from tkinter import ttk
import sys
sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from editabletable import GenericEditableTable, Mappings
except ImportError:
    print("couldn't import editabletable.")

class WV(ttk.Frame):

    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        root.title("Wohnungsverwaltung")
        # on resizing fill extra space:
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self._tree = None
        self._rechnungTableView: GenericEditableTable = None
        self._monatlicheTableView: GenericEditableTable = None
        self._sonstigeTableView: GenericEditableTable = None
        self._wohnungClickedCallback = None
        self.createUI(root)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def createUI(self, root):
        self._createMenu(root)
        self._createPanedWindow(root, 0, 0)
        self._createWohnungenTree(self._leftPane)
        self._createNotebook(self._rightPane)
        self._createStatusBar(root)

    def _createMenu(self, root):
        menu = Menu(root)
        root.config(menu=menu, relief=FLAT)

        filemenu = Menu(menu, tearoff=0, relief=FLAT)
        filemenu.add_command(label="Wohnungsübersicht drucken...")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="Anwendung", menu=filemenu)

        extrasmenu = Menu(menu, tearoff=0)
        extrasmenu.add_command(label="Verwalterwechsel...")
        extrasmenu.add_separator()
        extrasmenu.add_command(label="Jahresübersicht für Wohnung erstellen...")
        menu.add_cascade(label="Extras", menu=extrasmenu)

        anlvmenu = Menu(menu, tearoff=0)
        anlvmenu.add_command(label="Anlagen V für alle Wohnungen erstellen...")
        anlvmenu.add_command(label="Anlage V für ausgewählte Wohnung erstellen...")
        menu.add_cascade(label="Anlage V", menu=anlvmenu)

    def _createStatusBar(self, parent):
        sb = ttk.Label(parent, text='', relief=SUNKEN)
        sb.grid(column=0, row=1, sticky='swe')

        self._statusbar = sb

    def _createPanedWindow(self, parent, column: int, row: int):
        pw = ttk.PanedWindow(parent, orient=HORIZONTAL)
        pw.grid(column=column, row=row, sticky='nswe')
        self._panedWin = pw

        #left = ttk.Labelframe(pw, text='Alle Wohnungen', width=150)
        left = ttk.Frame(pw, width=150)
        left.grid(column=0, row=0, sticky='nswe')
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        pw.add(left)

        #right = ttk.Labelframe(pw, text='Daten der ausgewählten Wohnung')
        right = ttk.Frame(pw)
        right.grid(column=1, row=0, sticky='nswe')
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        pw.add(right)

        pw.rowconfigure(0, weight=1)
        pw.columnconfigure(0, weight=1)

        self._leftPane = left
        self._rightPane = right

    def _createWohnungenTree(self, parent):
        tree = ttk.Treeview(parent)
        tree['columns'] = ('whg_id')
        tree['displaycolumns'] = []
        tree.heading('#0', text='Übersicht', anchor=W)
        #tree.bind("<Button-1>", self._onTreeItemClicked)
        tree.bind('<<TreeviewSelect>>', self._onTreeItemClicked)
        tree.grid(column=0, row=0, sticky='nswe')
        self._tree = tree

    def _openBranches(self, tree, children):
        for child in children:
            tree.item(child, open=TRUE)
            childlist = tree.get_children(child)
            if childlist:
                self._openBranches(tree, childlist)

    def _createNotebook(self, parent):
        book = ttk.Notebook(parent)
        book.grid(column=0, row=0, sticky=(N,S,W,E))
        pages = (ttk.Frame(book), ttk.Frame(), ttk.Frame(),
                 ttk.Frame(), ttk.Frame())

        book.add(pages[0], text='Wohnung')
        book.add(pages[1], text='Rechnungen')
        book.add(pages[2], text='Monatliche Ein-/Auszahlungen')
        book.add(pages[3], text='Sonstige Ein-/Auszahlungen')
        book.add(pages[4], text='Mietverhältnis')
        book.columnconfigure(0, weight = 1)
        book.rowconfigure(0, weight=1)

        self._notebook = book

        self._createRechnungenTab(pages[1])
        self._createMonatlicheTab(pages[2])
        self._createSonstigeTab(pages[3])

    def _createRechnungenTab(self, rechnungPage:ttk.Frame):
        #Rechnung-Tabelle
        et = GenericEditableTable(rechnungPage)
        et.grid(column=0, row=0, sticky='nswe')
        self._rechnungTableView = et

        rechnungPage.rowconfigure(0, weight=1)
        rechnungPage.columnconfigure(0, weight=1)

    def _createMonatlicheTab(self, mietePage:ttk.Frame):
        #Miete-Tabelle
        et = GenericEditableTable(mietePage)
        et.grid(column=0, row=0, sticky='nswe')
        self._monatlicheTableView = et

        mietePage.rowconfigure(0, weight=1)
        mietePage.columnconfigure(0, weight=1)

    def _createSonstigeTab(self, sonstigePage: ttk.Frame):
        # Miete-Tabelle
        et = GenericEditableTable(sonstigePage)
        et.grid(column=0, row=0, sticky='nswe')
        self._sonstigeTableView = et

        sonstigePage.rowconfigure(0, weight=1)
        sonstigePage.columnconfigure(0, weight=1)

    def _createEditRow(self, column: int, row: int):
        pass

    def populateWohnungenTree(self, whg_list: list):
        # param whg_list: list of dictionaries.
        # A dictionary looks like so:
        #{
        # 'whg_id': '3',
        # 'plz': '90429',
        # 'ort': 'Nürnberg',
        # 'strasse': 'Austr. 22',
        # 'whg_bez': '2. OG'
        # }

        tree = self._tree
        top = tree.insert('', 0, text='Alle Wohnungen')
        ort =  stra = bez = ''
        ort_item = stra_item = bez_item = None
        for whg in whg_list:
            if whg['ort'] != ort:
               ort = whg['ort']
               ort_item = tree.insert(top, END, text=ort)
            if whg['strasse'] != stra:
                stra = whg['strasse']
                stra_item = tree.insert(ort_item, END, text=stra)
            tree.insert(stra_item, END, text = whg['whg_bez'], values=(whg['whg_id']))

        self._openBranches(tree, tree.get_children())

    def _onTreeItemClicked(self, event):  #bound to virtual TreeviewSelect event
        #item = self._tree.identify('item', event.x, event.y)
        item = self._tree.selection()
        dic = self._tree.item(item)
        try:
            whg_id: int = dic['values'][0]
            if whg_id > 0: #valid wohnung item clicked;
                self._callbackWohnungClicked(whg_id)
        except IndexError:  #straße- or ort-item clicked
           pass

    def _callbackWohnungClicked(self, whg_id:int) -> None:
        if self._wohnungClickedCallback:
            self._wohnungClickedCallback(whg_id)

    def registerWohnungClickCallback(self, callback):
        self._wohnungClickedCallback = callback

    def setStatusText(self, text: str):
        self._statusbar['text'] = text

    def configureMieteTable(self, columnDefs: list) -> None:
        self._monatlicheTableView.configureTable(columnDefs)

    def configureSonstigeTable(self, columnDefs: list) -> None:
        self._sonstigeTableView.configureTable(columnDefs)

    def getRechnungTableView(self) -> GenericEditableTable:
        return self._rechnungTableView

    def getMonatlicheTableView(self) -> GenericEditableTable:
        return self._monatlicheTableView

    def exitProgram(self):
        exit()

def main():
    import sys
    from wvcontroller import WvController
    print("path: ", sys.path)
    root = Tk()
    wv = WV(root)
    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    ctrl = WvController(wv)
    ctrl.startWork()

    wv.setStatusText("Bereit")

    #width = root.winfo_screenwidth()
    #width = root.winfo_width()
    #height = int(root.winfo_screenheight()/2)
    #root.geometry('%sx%s' % (900, height))

    root.mainloop()

if __name__ == '__main__':
    main()