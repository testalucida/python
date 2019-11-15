from tkinter import *
from tkinter import ttk
from interfaces import XWohnungDetails

try:
    from mywidgets import TextEntry, IntEntry, FloatEntry, MyLabel, MyCombobox
    from mycalendar import DateEntry
    import datehelper
except ImportError:
    print("couldn't import my widgets.")

class WohnungDetailsView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._details: XWohnungDetails = None
        self._lblIdent = None
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
        self._createUI()
        self.columnconfigure(0, weight=1)
        # Bemerkumg +++++++++++
        self._txtBemerkung = None

    def _createUI(self):
        padx = pady = 5
        self._lblIdent = self._createWohnungIdent(padx, pady)
        self._createAllgemeinFrame(1, padx, pady)
        self._createAusstattungFrame(2, padx, pady)
        self._createZubehoerFrame(3, padx, pady)
        self._createBemerkung(4, padx, pady)
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
        lf = ttk.Labelframe(self, text='Allgemeine Daten')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)

        col = 0
        cbo = MyCombobox(lf)
        cbo.setItems((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))
        cbo.setWidth(3)
        cbo.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        col += 1
        self._cboEtage = cbo
        MyLabel(lf, '. Etage', col, 0, 'nswe', 'w', (0,padx), pady)
        col += 1

        ie = IntEntry(lf)
        ie.setWidth(3)
        ie.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        col += 1
        self._ieQm = ie
        lbl = MyLabel(lf, 'qm', col, 0, 'nswe', 'w', (0,padx), pady)
        col += 1

        cbo = MyCombobox(lf)
        cbo.setItems((1, 1.5, 2, 2.5, 3, 3.5, 4, 5))
        cbo.setIndex(2)
        cbo.setWidth(3)
        cbo.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        col += 1
        self._cboZimmer = cbo
        MyLabel(lf, 'Zimmer', col, 0, 'nswe', 'w', (0,padx), pady)
        col += 1

        ie = IntEntry(lf)
        ie.setWidth(3)
        ie.grid(column=col, row=0, sticky='nswe', padx=padx, pady=pady)
        col += 1
        self._ieAnteil = ie
        MyLabel(lf, 'Anteile am Gesamtobjekt', col, 0, 'nswe', 'w', (0,padx), pady)

        lbl = MyLabel(lf, 'IBAN der WEG ', 0, 1, 'nswe', 'w', padx, pady)
        lbl.grid(columnspan=2)
        te = TextEntry(lf, 2, 1,'nswe', (padx), pady )
        te.grid(columnspan=5)
        self._teIbanWEG = te

    def _createAusstattungFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Ausstattung der Wohnung')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)
        self._createKuecheLabelframe(lf, padx, pady)
        self._createBadLabelframe(lf, padx, pady)

    def _createKuecheLabelframe(self, parent, padx, pady):
        lfKueche = ttk.Labelframe(parent, text='Küche')
        lfKueche.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        c = r = 0
        padx = (1, padx)
        ##### Art der Küche
        MyLabel(lfKueche, 'Küche ist', c, r, 'nswe', 'w', padx, pady)
        c += 1
        cbo = MyCombobox(lfKueche)
        cbo.setItems(('', 'Küchenzeile im Wohnraum', 'eigener Raum', 'Wohnküche'))
        cbo.setIndex(0)
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
        cbo.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cboKuechenGeraete = cbo

    def _createBadLabelframe(self, parent, padx, pady):
        lfBad = ttk.Labelframe(parent, text='Bad')
        lfBad.grid(column=1, row=0, sticky='nswe', padx=padx, pady=pady)
        c = r = 0
        padx = (1, padx)

    def _createZubehoerFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Weitere Merkmale der Wohnung')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)
        c = r = 0
        padx = (1, padx)

        ########### Balkon
        MyLabel(lf, 'Balkon: ', c, r, 'nswe', 'w', padx, pady)
        c += 1
        cbo = MyCombobox(lf)
        cbo.setItems(('', 'Keiner', 'Nord', 'Ost', 'Süd', 'West'))
        cbo.setWidth(7)
        cbo.setIndex(0)
        cbo.grid(column=c, row=r, sticky='nswe', padx=padx, pady=pady)
        self._cboBalkon = cbo

    def _createBemerkung(self, row, padx, pady):
        pass

    def _createButtons(self, row, padx, pady):
        pass

    def setData(self, details: XWohnungDetails):
        self._details = details
        bez = details.ort + ', ' + details.strasse +  ', ' + details.whg_bez
        self._lblIdent.setValue(bez)

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

