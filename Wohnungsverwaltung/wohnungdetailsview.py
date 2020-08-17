from tkinter import *
from tkinter import ttk
from interfaces import XWohnungDetails

# print ('wohnungdetailsview.py: sys.path: ', sys.path)

try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, MyCombobox, MyText
    from mycalendar import DateEntry
    import datehelper
except ImportError as err:
    print("wohnungdetailsview.py: couldn't import my widgets: ", err )

class WohnungDetailsView (ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._details: XWohnungDetails = None
        self._lblIdent = None

        self._style_labelframe = None
        self._stylename_labelframe = None

        # Allgemein +++++++++++
        self._cboEtage = None
        self._ieAnteil = None
        self._teIbanWEG = None
        self._cboZimmer = None
        self._ieQm = None
        #Ausstattung +++++++++++
        self._cboKueche = None
        self._cbEbk = None
        self._ivarEbk = IntVar()
        self._cboKuechenGeraete = None
        self._cbTageslichtbad = None
        self._ivarTageslicht = IntVar()
        self._cbDusche = None
        self._ivarDusche = IntVar()
        self._cbWanne = None
        self._ivarWanne = IntVar()
        self._cbBidet = None
        self._ivarBidet = IntVar()
        self._cboHeizung = None
        # Zubehör +++++++++++++
        self._cboBalkon = None
        self._cbKellerabteil = None
        self._ivarKellerabteil = IntVar()
        self._cboGarage = None
        self._cbAufzug = None
        self._ivarAufzug = IntVar()
        # Bemerkumg +++++++++++
        self._txtBemerkung = None
        # Buttons ++++++++++++++
        self._btnOk = None
        # called after any modification
        self._isModified = False
        self._saveCallback = None

        self.columnconfigure(0, weight=1)
        self._createUI()
        self._setIntVarTracebacks()

    def registerSaveCallback(self, cbfunc):
        #function to be called back has to accept
        # 1 Argument: XWohnnungDetails
        self._saveCallback = cbfunc

    def _setIntVarTracebacks(self):
        d = self.__dict__
        for k, v in d.items():
            if isinstance(v, IntVar):
                v.trace('w', self._onModified)

    def _onModified(self, *args):
        self._isModified = True
        self.setOkButtonEnabled(True)

    def setOkButtonEnabled(self, enabled: bool):
        self._btnOk['state'] = 'normal' if enabled else 'disabled'

    def _createUI(self):
        padx = pady = 5
        self._lblIdent = self._createWohnungIdent(padx, pady)
        self._style_labelframe = ttk.Style()
        self._style_labelframe.\
            configure('my.TLabelframe.Label', font=('courier', 13, 'bold'))
        self._createAllgemeinFrame(1, padx, pady)
        self._createAusstattungFrame(2, padx, pady)
        self._createZubehoerFrame(3, padx, pady)
        self._createBemerkungFrame(4, padx, pady)
        self._createButtons(5, padx, pady)

    def _createWohnungIdent(self, padx, pady) -> ttk.Label:
        lbl = MyLabel(self, text='', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady)
        lbl.setBackground('whg_short.TLabel', 'gray')
        lbl.setForeground('whg_short.TLabel', 'white')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('whg_short.TLabel', 10, 10)
        return lbl

    def _createAllgemeinFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Allgemeine Daten', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=(pady+8, pady))

        ### Combo und Label für Etage
        col = 0
        cbo = MyCombobox(lf)
        cbo.setItems((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
        cbo.setWidth(3)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)

        col += 1
        self._cboEtage = cbo
        MyLabel(lf, '. Etage', col, 0, 'nswe', 'w', (0,padx), pady)

        #### Entry und Label für qm
        col += 1
        ie = IntEntry(lf)
        ie.setWidth(3)
        ie.registerModifyCallback(self._onModified)
        ie.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        self._ieQm = ie

        col += 1
        lbl = MyLabel(lf, 'qm', col, 0, 'nswe', 'w', (0,padx), pady)

        ### Combo und Label für Zimmer
        col += 1
        cbo = MyCombobox(lf)
        cbo.setItems((1, 1.5, 2, 2.5, 3, 3.5, 4, 5))
        cbo.setIndex(2)
        cbo.setWidth(3)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        self._cboZimmer = cbo

        col += 1
        MyLabel(lf, 'Zimmer', col, 0, 'nswe', 'w', (0,padx), pady)

        ### Entry und Label für Anteile
        col += 1
        ie = IntEntry(lf)
        ie.setWidth(3)
        ie.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        ie.registerModifyCallback(self._onModified)
        self._ieAnteil = ie

        col += 1
        MyLabel(lf, 'Anteile am Gesamtobjekt', col, 0, 'nswe', 'w', (0,padx), pady)

        ### neue Zeile
        ### Checkbutton für Aufzug
        col = 0
        cb = ttk.Checkbutton(lf, text='Aufzug im Haus', variable=self._ivarAufzug)
        cb.grid(column=col, row=1, columnspan=2, sticky='nswe', padx=padx, pady=pady)
        self._cbAufzug = cb

        ### neue Zeile
        ### Label und Entry für IBAN
        col = 0
        lbl = MyLabel(lf, 'IBAN der WEG ', 0, 2, 'nswe', 'w', padx, pady)
        lbl.grid(columnspan=2)

        col += 2
        te = TextEntry(lf, col, 2,'nswe', (padx), pady )
        te.registerModifyCallback(self._onModified)
        te.grid(columnspan=5)
        self._teIbanWEG = te

    def _createAusstattungFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Ausstattung der Wohnung', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=(pady+8, pady))
        self._createKuecheLabelframe(lf, padx, pady)
        self._createBadLabelframe(lf, padx, pady)
        self._createHeizungFrame(lf, 1, padx, pady)

    def _createKuecheLabelframe(self, parent, padx, pady):
        s = ttk.Style()
        s.configure('ital.TLabelframe.Label', font=('courier', 13, 'italic'))
        lfKueche = ttk.Labelframe(parent, text='Küche', style='ital.TLabelframe')
        lfKueche.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        c = r = 0
        padx = (1, padx)

        ##### Art der Küche
        MyLabel(lfKueche, 'Küche ist', c, r, 'nswe', 'w', padx, pady)
        c += 1
        cbo = MyCombobox(lfKueche)
        cbo.setItems(('', 'Küchenzeile im Wohnraum', 'eigener Raum', 'Wohnküche'))
        cbo.setIndex(0)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=c, row=r, columnspan=3, sticky='nswe', padx=padx, pady=pady)
        self._cboKueche = cbo

        ########## Einbauküche? Mit welchen Geräten?
        c = 0
        r = 1
        cb = ttk.Checkbutton(lfKueche, text='Einbauküche', variable=self._ivarEbk)
        cb.grid(column=c, row=r, columnspan=2, sticky='nswe', padx=padx, pady=pady)
        self._cbEbk = cb

        c += 2
        MyLabel(lfKueche, 'Geräte:', c, r, 'nswe', 'w', padx, pady)
        c += 1
        cbo = MyCombobox(lfKueche)
        cbo.setItems(('', 'Keine', 'Herd', 'Herd, Kühlschrank',
                      'Herd, Kühlschrank, Geschirrspüler'))
        cbo.setWidth(26)
        cbo.setIndex(0)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cboKuechenGeraete = cbo

    def _createBadLabelframe(self, parent, padx, pady):
        lfBad = ttk.Labelframe(parent, text='Bad', style='ital.TLabelframe')
        lfBad.grid(column=1, row=0, sticky='nswe', padx=padx, pady=pady)
        c = r = 0
        padx = (1, padx)

        cb = ttk.Checkbutton(lfBad, text='Tageslichtbad', variable=self._ivarTageslicht)
        cb.grid(column=c, row=r, columnspan=2, sticky='nswe', padx=padx, pady=pady)
        self._cbTageslichtbad

        r += 1
        cb = ttk.Checkbutton(lfBad, text='Dusche', variable=self._ivarDusche)
        cb.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cbDusche

        c += 1
        cb = ttk.Checkbutton(lfBad, text='Wanne', variable=self._ivarWanne)
        cb.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cbWanne

        c += 1
        cb = ttk.Checkbutton(lfBad, text='Bidet', variable=self._ivarBidet)
        cb.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cbBidet

    def _createHeizungFrame(self, lf, row, padx, pady) -> None:
        f = ttk.Frame(lf)
        f.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)

        padx = (0, padx)
        MyLabel(f, 'Heizung:', 0, 0, 'nswe', 'w', padx, pady)
        cbo = MyCombobox(f)
        cbo.setItems(('', 'Gas-Etagenheizung', 'Oel Zentral',
                      'Gas Zentral', 'Fernwaerme', 'Nachtspeicher'))
        cbo.setIndex(1)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=1, row=0, sticky='nswe', padx=padx, pady=pady)
        self._cboHeizung = cbo

    def _createZubehoerFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Weitere Merkmale der Wohnung', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=(pady+8, pady))
        c = r = 0
        padx = (1, padx)

        ########### Balkon
        MyLabel(lf, 'Balkon: ', c, r, 'nsw', 'w', padx, pady)
        c += 1
        cbo = MyCombobox(lf)
        cbo.setItems(('', 'Keiner', 'Nord', 'Ost', 'Süd', 'West'))
        cbo.setWidth(7)
        cbo.setIndex(0)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cboBalkon = cbo

        c += 1
        cb = ttk.Checkbutton(lf, text='Kellerabteil', variable=self._ivarKellerabteil)
        cb.grid(column=c, row=r, sticky='nswe', padx=(28, 5), pady=pady)
        self._cbKellerabteil = cb

        c += 1
        MyLabel(lf, 'Garage: ', c, r, 'nswe', 'w', (28, 5), pady)
        c += 1
        cbo = MyCombobox(lf)
        cbo.setItems(('', 'Keine', 'Stellplatz', 'TG-Stellplatz', 'Garage'))
        cbo.setWidth(13)
        cbo.setIndex(0)
        cbo.registerModifyCallback(self._onModified)
        cbo.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cboGarage = cbo

    def _createBemerkungFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Sonstiges', style='my.TLabelframe')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=(pady + 8, pady))
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

    def _createButtons(self, row, padx, pady):
        btn = ttk.Button(self, text='Speichern', command=self._onSave)
        btn.grid(column=0, row=row, sticky='ne', padx=padx, pady=pady)
        self._btnOk = btn
        self.setOkButtonEnabled(False)

    def _onSave(self):
        if self._saveCallback:
            data = self.getData()
            self._saveCallback(data)
        self.setOkButtonEnabled(False)

    def setData(self, details: XWohnungDetails):
        self._details = details
        bez = details.ort + ', ' + details.strasse +  ', ' + details.whg_bez
        self._lblIdent.setValue(bez)

        self._cboEtage.setValue(details.etage)
        self._ieAnteil.setValue(details.anteil)
        self._teIbanWEG.setValue(details.iban_weg)
        self._cboZimmer.setValue(details.zimmer)
        self._ieQm.setValue(details.qm)
        # Ausstattung +++++++++++
        self._cboKueche.setValue(details.kueche)
        self._ivarEbk.set(1 if details.ebk == 'J' else 0)
        self._cboKuechenGeraete.setValue(details.kuechengeraete)
        self._ivarTageslicht.set(1 if details.tageslichtbad == 'J' else 0)
        self._ivarDusche.set(1 if details.dusche == 'J' else 0)
        self._ivarWanne.set(1 if details.badewanne == 'J' else 0)
        self._ivarBidet.set(1 if details.bidet == 'J' else 0)
        self._cboHeizung.setValue(details.heizung)
        # Zubehör +++++++++++++
        self._cboBalkon.setValue(details.balkon)
        self._ivarKellerabteil.set(1 if details.kellerabteil == 'J' else 0)
        self._cboGarage.setValue(details.garage)
        self._ivarAufzug.set(1 if details.aufzug == 'J' else 0)
        # Bemerkumg +++++++++++
        self._txtBemerkung.setValue(details.bemerkung)

        self.setOkButtonEnabled(False)
        self._isModified = False

    def getData(self) -> XWohnungDetails:
        d = self._details
        d.etage = self._cboEtage.getValue()
        d.anteil = self._ieAnteil.getValue()
        d.iban_weg = self._teIbanWEG.getValue()
        d.zimmer = self._cboZimmer.getValue()
        d.kueche = self._cboKueche.getValue()
        d.ebk = 'J' if self._ivarEbk.get() > 0 else 'N'
        d.kuechengeraete = self._cboKuechenGeraete.getValue()
        d.balkon = self._cboBalkon.getValue()
        d.heizung = self._cboHeizung.getValue()
        d.qm = self._ieQm.getValue()
        d.bemerkung = self._txtBemerkung.getValue()
        d.tageslichtbad = 'J' if self._ivarTageslicht.get() > 0 else 'N'
        d.badewanne = 'J' if self._ivarWanne.get() > 0 else 'N'
        d.dusche = 'J' if self._ivarDusche.get() > 0 else 'N'
        d.bidet = 'J' if self._ivarBidet.get() > 0 else 'N'
        d.kellerabteil = 'J' if self._ivarKellerabteil.get() > 0 else 'N'
        d.aufzug = 'J' if self._ivarAufzug.get() > 0 else 'N'
        d.garage = self._cboGarage.getValue()
        return d

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('test')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    wv = WohnungDetailsView(root)
    wv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    test()

