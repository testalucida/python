from tkinter import *
from tkinter import ttk

try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, MyCombobox, MyText
    from mycalendar import DateEntry
    import datehelper
except ImportError:
    print("couldn't import my widgets.")

class MietverhaeltnisView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._lblIdent = None
        self._cboAnrede = None # todo
        self._teName = None
        self._teVorname = None
        self._teAusweisId = None
        self._teTelefon = None
        self._teMailto = None
        self._teIban = None
        self._deVermietetAb = None
        self._deVermietetBis = None
        self._ieKaution = None
        self._teAngelegtBei = None
        self._txtBemerkung = None
        self._btnOk = None
        self._style_labelframe = None
        self._saveCallback = None

        self.columnconfigure(0, weight=1)
        self._createUI()

    def _createUI(self):
        padx = 10
        pady = 5
        self._lblIdent = self._createWohnungIdent(padx, pady)
        self._style_labelframe = ttk.Style()
        self._style_labelframe.\
            configure('my.TLabelframe.Label', font=('courier', 13, 'bold'))

        self._createMieterFrame(1, 10, 15, 10)
        self._createMietvertragFrame(2, 10, 15, 10)
        self._createBemerkung(3, 10, 15, 10)
        self._createButtons(4, 10, 10, 10)

    def _createWohnungIdent(self, padx, pady) -> ttk.Label:
        lbl = MyLabel(self, text='', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady)
        lbl.setBackground('whg_short.TLabel', 'gray')
        lbl.setForeground('whg_short.TLabel', 'white')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('whg_short.TLabel', 10, 10)
        return lbl

    def _createMieterFrame(self, row, xmargins: int, topmargin: int, bottommargin: int):
        padx=xmargins
        pady=(topmargin, bottommargin)
        lf = ttk.Labelframe(self, text='Mieter', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)

        padx=(5,6)
        pady=(5,5)
        col = row = 0
        ######### Anrede
        MyLabel(lf, 'Anrede:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        cbo = MyCombobox(lf)
        cbo.setItems(('Frau', 'Herr'))
        cbo.setWidth(4)
        cbo.grid(column=col, row=row, sticky='nsw', padx=padx, pady=pady)
        self._cboAnrede = cbo
        ######### Name
        col += 1
        MyLabel(lf, 'Name:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)

        ######### Vorname
        col += 1
        MyLabel(lf, 'Vorname:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)

        ######### Perso-Nr.
        row += 1
        col = 0
        MyLabel(lf, 'Personalausweis-Nr.:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)

        ######## Telefon
        row += 1
        col = 0
        MyLabel(lf, 'Telefon:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)

        ######### mailto
        col += 1
        MyLabel(lf, 'Mailto:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.grid(columnspan=2)

        ######## Bankverbindung
        row += 1
        col = 0
        MyLabel(lf, 'IBAN:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.grid(columnspan=2)

    def _createMietvertragFrame(self, row, xmargins: int, topmargin: int, bottommargin: int):
        padx=xmargins
        pady=(topmargin, bottommargin)
        lf = ttk.Labelframe(self, text='Mietvertrag', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)

        padx = (5, 6)
        pady = (5, 5)
        ######### Vermietung ab
        col = row = 0
        MyLabel(lf, 'Vermietung ab:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        de = DateEntry(lf)
        de.grid(column=col, row=row, sticky='nswe', padx=padx, pady=pady)
        de.setWidth(10)

        ######### Vermietung befristet bis
        col += 1
        MyLabel(lf, 'befristet bis:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        de = DateEntry(lf)
        de.grid(column=col, row=row, sticky='nsw', padx=padx, pady=pady)
        de.setWidth(10)

        ######## Kaution
        row += 1
        col = 0
        MyLabel(lf, 'Kaution:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        ie = IntEntry(lf)
        ie.grid(column=col, row=row, sticky='nswe', padx=padx, pady=pady)
        ie.setWidth(5)

        ######### bei welcher Bank
        col += 1
        MyLabel(lf, 'hinterlegt bei:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)

    def _createBemerkung(self, row, xmargins: int, topmargin: int, bottommargin: int):
        padx = xmargins
        pady = (topmargin, bottommargin)
        lf = ttk.Labelframe(self, text='Sonstiges', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)
        lf.columnconfigure(0, weight=1)

        padx = (1, padx)
        txt = MyText(lf)
        txt['height'] = 3
        txt.registerModifyCallback(self._onModified)
        txt.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)

        scrollb = ttk.Scrollbar(lf, command=txt.yview)
        scrollb.grid(column=1, row=0, sticky='nsew')
        txt['yscrollcommand'] = scrollb.set

        self._txtBemerkung = txt

    def _createButtons(self, row, rightmargin: int, topmargin: int, bottommargin: int):
        padx=(0, rightmargin)
        pady=(topmargin, bottommargin)
        btn = ttk.Button(self, text='Speichern', command=self._onSave)
        btn.grid(column=0, row=row, sticky='ne', padx=padx, pady=pady)
        self._btnOk = btn
        self.setOkButtonEnabled(False)

    def _onModified(self, *args):
        self._isModified = True
        self.setOkButtonEnabled(True)

    def _onSave(self):
        print('save')

    def registerSaveCallback(self, cbfunc):
        #function to be called back has to accept
        # 1 Argument: XMietverhaeltnis
        self._saveCallback = cbfunc

    def setOkButtonEnabled(self, enabled: bool):
        self._btnOk['state'] = 'normal' if enabled else 'disabled'

def test():
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    mv = MietverhaeltnisView(root)
    mv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    test()

