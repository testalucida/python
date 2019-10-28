from tkinter import *
from tkinter import ttk
from enum import Enum, IntEnum
import sys
sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from editabletable import GenericEditableTable, Mappings
    from stammdatenview import StammdatenView
    from veranlagungview import VeranlagungView
except ImportError:
    print("couldn't import some stuff.")

WohnungAction = IntEnum('WohnungAction', 'new edit delete')

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
        self._grundsteuerTableView: GenericEditableTable = None
        self._stammdatenView: StammdatenView = None
        self._veranlagungView: VeranlagungView = None
        self._wohnungClickedCallback = None
        self._wohnungActionCallback = None
        self._createUI(root)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def _createUI(self, root):
        self._createMenu(root)
        self._createPanedWindow(root, 0, 0)
        self._createWohnungenTree(self._leftPane)
        self._createNotebook(self._rightPane)
        self._createStatusBar(root)

    def _createMenu(self, root):
        menu = Menu(root)
        root.config(menu=menu, relief=FLAT)

        filemenu = Menu(menu, tearoff=0, relief=FLAT)
        filemenu.add_command(label="Neues Objekt anlegen...", command=self._onNewWohnung)
        filemenu.add_command(label="Objekt löschen...", command=self._onDeleteWohnung)
        filemenu.add_command(label="Objektübersicht drucken...")
        filemenu.add_separator()
        filemenu.add_command(label="Vermieter verwalten...")
        filemenu.add_command(label="Verwalter verwalten...")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="Stammdaten", menu=filemenu)

        extrasmenu = Menu(menu, tearoff=0)
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
        tree.column("#0", minwidth=100, width=275)
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
        PAGE_STAMMDATEN = 0
        PAGE_WOHNUNG = 1
        PAGE_RECHUNGEN = 2
        PAGE_MTL_EIN_AUS = 3
        PAGE_SONST_EIN_AUS = 4
        PAGE_MIETEVERHAELTNIS = 5
        PAGE_VERANLAGUNG = 6

        book = ttk.Notebook(parent)
        book.grid(column=0, row=0, sticky=(N,S,W,E))
        pages = (ttk.Frame(), ttk.Frame(), ttk.Frame(),
                 ttk.Frame(), ttk.Frame(), ttk.Frame(), ttk.Frame())

        book.add(pages[PAGE_STAMMDATEN], text='Stammdaten')
        book.add(pages[PAGE_WOHNUNG], text='Wohnung')
        book.add(pages[PAGE_RECHUNGEN], text='Rechnungen')
        book.add(pages[PAGE_MTL_EIN_AUS], text='Monatliche Ein-/Auszahlungen')
        book.add(pages[PAGE_SONST_EIN_AUS], text='Sonstige Ein-/Auszahlungen')
        book.add(pages[PAGE_MIETEVERHAELTNIS], text='Mietverhältnis')
        book.add(pages[PAGE_VERANLAGUNG], text='Veranlagung')
        book.columnconfigure(0, weight = 1)
        book.rowconfigure(0, weight=1)

        self._notebook = book

        self._createStammdatenTab(pages[PAGE_STAMMDATEN])
        self._createRechnungenTab(pages[PAGE_RECHUNGEN])
        self._createMonatlicheTab(pages[PAGE_MTL_EIN_AUS])
        self._createSonstigeTab(pages[PAGE_SONST_EIN_AUS])
        self._createVeranlagungTab(pages[PAGE_VERANLAGUNG])

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
        # sonstige payments and grundsteuer

        lbl = ttk.Label(sonstigePage, text='Einmalige Ein- und Auszahlungen')
        lbl.configure(anchor="center", background='lightyellow')
        lbl.grid(column=0, row=0, sticky='we', pady=(20,2))

        et = GenericEditableTable(sonstigePage)
        et.grid(column=0, row=1, sticky='nswe')
        self._sonstigeTableView = et

        lbl = ttk.Label(sonstigePage, text='Grundsteuer')
        lbl.configure(anchor="center", background='lightyellow')
        lbl.grid(column=0, row=2, sticky='we', pady=(20,2))

        gset = GenericEditableTable(sonstigePage)
        gset.grid(column=0, row=3, sticky='nswe')
        self._grundsteuerTableView = gset

        sonstigePage.rowconfigure(1, weight=1)
        sonstigePage.rowconfigure(3, weight=1)
        sonstigePage.columnconfigure(0, weight=1)

    def _createStammdatenTab(self, stammdatenPage:ttk.Frame):
        stv = StammdatenView(stammdatenPage)
        stv.grid(column=0, row=0, sticky='nwe', padx=50, pady=50)
        self._stammdatenView = stv

        stammdatenPage.rowconfigure(0, weight=1)
        stammdatenPage.columnconfigure(0, weight=1)

    def _createVeranlagungTab(self, veranlPage: ttk.Frame):
        vv = VeranlagungView(veranlPage)
        vv.grid(column=1, row=1, sticky='nswe', padx=5, pady=5)
        self._veranlagungView = vv

        # veranlPage.rowconfigure(0, weight=1)
        # veranlPage.rowconfigure(2, weight=3)
        veranlPage.columnconfigure(0, weight=1)
        veranlPage.columnconfigure(2, weight=1)

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
        tree.delete(*tree.get_children())
        self.hauspng = PhotoImage(file="/home/martin/Projects/python/Wohnungsverwaltung/images/haus_18x16.png")
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
            tree.insert(stra_item, END, text = whg['whg_bez'], image=self.hauspng, values=(whg['whg_id']))

        self._openBranches(tree, tree.get_children())

    def _onTreeItemClicked(self, event):  #bound to virtual TreeviewSelect event
        whg_id = self.getSelectedTreeItem()
        if whg_id > 0:
            self._callbackWohnungClicked(whg_id)

    def _onNewWohnung(self):
        self._doWohnungActionCallback(WohnungAction.new)

    def _onDeleteWohnung(self):
        self._doWohnungActionCallback(WohnungAction.delete)

    def _doWohnungActionCallback(self, action: WohnungAction):
        if self._wohnungActionCallback:
            whg_id = -1
            if not action == WohnungAction.new:
                whg_id = self.getSelectedTreeItem()
            self._wohnungActionCallback(whg_id, action)

    def getSelectedTreeItem(self) -> int:
        item = self._tree.selection()
        dic = self._tree.item(item)
        try:
            whg_id: int = dic['values'][0]
            if whg_id > 0:  # valid wohnung item clicked;
                return whg_id
        except IndexError:  # straße- or ort-item clicked
            return -1

    def selectWohnungItem(self, whg_id: int) -> None:
        item = self.searchWohnungItem(whg_id, self._tree.get_children())
        self._tree.selection_set(item)
        self._tree.focus(item)

    def searchWohnungItem(self, whg_id: int, children):
        for child in children:
            childlist = self._tree.get_children(child)
            if childlist:
                item = self.searchWohnungItem(whg_id, childlist)
                if item:
                    return item
            else:
                dic = self._tree.item(child)
                ival = int(dic['values'][0])
                if ival == whg_id:
                    return child
                return None

    def _callbackWohnungClicked(self, whg_id:int) -> None:
        if self._wohnungClickedCallback:
            self._wohnungClickedCallback(whg_id)

    def setNotebookTab(self, idx: int) -> None:
        self._notebook.select(idx)

    def registerWohnungClickCallback(self, callback):
        self._wohnungClickedCallback = callback

    def registerWohnungActionCallback(self, callback):
        self._wohnungActionCallback = callback

    def setStatusText(self, text: str):
        self._statusbar['text'] = text

    def getRechnungTableView(self) -> GenericEditableTable:
        return self._rechnungTableView

    def getSonstigeTableView(self) -> GenericEditableTable:
        return self._sonstigeTableView

    def getGrundsteuerTableView(self) -> GenericEditableTable:
        return self._grundsteuerTableView

    def getMonatlicheTableView(self) -> GenericEditableTable:
        return self._monatlicheTableView

    def getStammdatenView(self) -> StammdatenView:
        return self._stammdatenView

    def getVeranlagungView(self) -> VeranlagungView:
        return self._veranlagungView

    def exitProgram(self):
        exit()

def main():
    import sys
    from wvcontroller import WvController
    print("path: ", sys.path)
    root = Tk()

    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    wv = WV(root)
    wv.setNotebookTab(0)

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