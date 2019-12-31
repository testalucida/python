from tkinter import *
from tkinter import ttk
from interfaces import XMietverhaeltnis

try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, \
        MyCombobox, MyText
    from mycalendar import DateEntry
    import datehelper
except ImportError:
    print("couldn't import my widgets.")

class MietverhaeltnisView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._data: XMietverhaeltnis = None
        self._lblIdent = None
        self._cboAnrede = None
        self._teName = None
        self._teVorname = None
        self._teGeboren_am = None
        self._teAusweisId = None
        self._teTelefon = None
        self._teMailto = None
        self._teIban = None
        self._deVermietetAb = None
        self._deVermietetBis = None
        self._ieKaution = None
        self._teAngelegtBei = None
        self._txtInseratText = None
        self._teInseriertBei = None
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
        self._createInseratText(3, 10, 15, 10)
        self._createBemerkung(4, 10, 15, 10)
        self._createButtons(5, 10, 10, 10)

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
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=col, row=row, sticky='nsw', padx=padx, pady=pady)
        self._cboAnrede = cbo

        ######### Name
        col += 1
        MyLabel(lf, 'Name:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.registerModifyCallback(self._onModified)
        self._teName = te

        ######### Vorname
        col += 1
        MyLabel(lf, 'Vorname:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.registerModifyCallback(self._onModified)
        self._teVorname = te

        ######### Geburtstag
        row += 1
        col = 0
        MyLabel(lf, 'Geburtstag:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.registerModifyCallback(self._onModified)
        self._teGeboren_am = te

        ######### Perso-Nr.
        col += 1
        MyLabel(lf, 'Personalausweis-Nr.:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.grid(columnspan=2)
        te.registerModifyCallback(self._onModified)
        self._teAusweisId = te

        ######## Telefon
        row += 1
        col = 0
        MyLabel(lf, 'Telefon:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.registerModifyCallback(self._onModified)
        self._teTelefon = te

        ######### mailto
        col += 1
        MyLabel(lf, 'Mailto:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.grid(columnspan=2)
        te.registerModifyCallback(self._onModified)
        self._teMailto = te

        ######## Bankverbindung
        row += 1
        col = 0
        MyLabel(lf, 'IBAN:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.registerModifyCallback(self._onModified)
        te.grid(columnspan=2)
        self._teIban = te

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
        de.registerModifyCallback(self._onModified)
        de.grid(column=col, row=row, sticky='nswe', padx=padx, pady=pady)
        de.setWidth(10)
        self._deVermietetAb = de

        ######### Vermietung befristet bis
        col += 1
        MyLabel(lf, 'befristet bis:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        de = DateEntry(lf)
        de.registerModifyCallback(self._onModified)
        de.grid(column=col, row=row, sticky='nsw', padx=padx, pady=pady)
        de.setWidth(10)
        self._deVermietetBis = de

        ######## Kaution
        row += 1
        col = 0
        MyLabel(lf, 'Kaution:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        ie = IntEntry(lf)
        ie.registerModifyCallback(self._onModified)
        ie.grid(column=col, row=row, sticky='nswe', padx=padx, pady=pady)
        ie.setWidth(5)
        self._ieKaution = ie

        ######### bei welcher Bank
        col += 1
        MyLabel(lf, 'hinterlegt bei:', col, row, 'nswe', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nswe', padx, pady)
        te.registerModifyCallback(self._onModified)
        self._teAngelegtBei = te

    def _createInseratText(self, row, xmargins: int, topmargin: int, bottommargin: int):
        padx = xmargins
        pady = (topmargin, bottommargin)
        lf = ttk.LabelFrame(self, text='Inserat', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)
        lf.columnconfigure(1, weight=1)
        lf.columnconfigure(3, weight=1)
        row = col = 0
        MyLabel(lf, 'Text:', col, row, 'nw', 'w', padx, pady)
        col += 1
        txt = MyText(lf)
        txt['height'] = 6
        txt['width'] = 50
        txt.registerModifyCallback(self._onModified)
        txt.grid(column=col, row=row, sticky='nswe', padx=padx, pady=pady)
        self._txtInseratText = txt

        col += 1
        MyLabel(lf, 'inseriert bei:', col, row, 'nw', 'w', padx, pady)
        col += 1
        te = TextEntry(lf, col, row, 'nwe', padx, pady)
        te.registerModifyCallback(self._onModified)
        self._teInseriertBei = te

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
        if self._saveCallback:
            data = self.getData()
            self._saveCallback(data)
        self._isModified = False
        self.setOkButtonEnabled(False)

    def setData(self, data: XMietverhaeltnis):
        self._data = data
        self._lblIdent.setValue(data.ort + ', ' +
                                data.strasse + ' ' + data.whg_bez)
        self._cboAnrede.setValue(data.anrede)
        self._teName.setValue(data.name)
        self._teVorname.setValue(data.vorname)
        self._teGeboren_am.setValue(data.geboren_am)
        self._teAusweisId.setValue(data.ausweis_id)
        self._teTelefon.setValue(data.telefon)
        self._teMailto.setValue(data.mailto)
        self._teIban.setValue(data.iban)
        if data.vermietet_ab:
            self._deVermietetAb.setValue(data.vermietet_ab)
        if data.vermietet_bis:
            self._deVermietetBis.setValue(data.vermietet_bis)
        self._ieKaution.setValue(data.kaution)
        self._teAngelegtBei.setValue(data.kaution_angelegt_bei)
        if data.inserat_text:
            self._txtInseratText.setValue(data.inserat_text)
        if data.inseriert_bei:
            self._teInseriertBei.setValue(data.inseriert_bei)
        self._txtBemerkung.setValue(data.bemerkung)
        self._isModified = False
        self.setOkButtonEnabled(False)

    def getData(self) -> XMietverhaeltnis:
        data = self._data
        data.anrede = self._cboAnrede.getValue()
        data.name = self._teName.getValue()
        data.vorname = self._teVorname.getValue()
        data.geboren_am = self._teGeboren_am.getValue()
        data.ausweis_id = self._teAusweisId.getValue()
        data.telefon = self._teTelefon.getValue()
        data.mailto = self._teMailto.getValue()
        data.iban = self._teIban.getValue()
        data.vermietet_ab = self._deVermietetAb.getValue()
        data.vermietet_bis = self._deVermietetBis.getValue()
        data.kaution = self._ieKaution.getValue()
        data.kaution_angelegt_bei = self._teAngelegtBei.getValue()
        data.inserat_text = self._txtInseratText.getValue()
        data.inseriert_bei = self._teInseriertBei.getValue()
        data.bemerkung = self._txtBemerkung.getValue()
        return data

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

