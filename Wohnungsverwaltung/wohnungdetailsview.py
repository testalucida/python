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
        self._ieAnteil = None
        self._teIbanWEG = None
        self._cboZimmer = None
        self._ieQm = None
        #Ausstattung +++++++++++
        self._cbEbk = None
        self._ivarBalkon = IntVar()
        self._cbBalkon = None
        self._cbTageslichtbad = None
        self._cbDusche = None
        self._cbWanne = None
        self._cbBidet = None
        self._txtHeizung = None
        # Zubehör +++++++++++++
        self._cbKellerabteil = None
        self._cboGarage = None
        self._cbAufzug = None
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

        ie = IntEntry(lf)
        ie.setWidth(3)
        ie.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._ieQm = ie
        lbl = MyLabel(lf, 'qm', 1, 0, 'nswe', 'w', (0,padx), pady)

        cbo = MyCombobox(lf)
        cbo.setItems((1, 1.5, 2, 2.5, 3, 3.5, 4, 5))
        cbo.setIndex(2)
        cbo.setWidth(3)
        cbo.grid(column=2, row=0, sticky='nswe', padx=padx, pady=pady)
        self._cboZimmer = cbo
        MyLabel(lf, 'Zimmer', 3, 0, 'nswe', 'w', (0,padx), pady)
        # todo
        # Zimmer in der DB von int auf float ändern;
        # Select/Update im php Programm überprüfen
        # XWohnungDetails überprüfen

        ie = IntEntry(lf)
        ie.setWidth(3)
        ie.grid(column=4, row=0, sticky='nswe', padx=padx, pady=pady)
        self._ieAnteil = ie
        MyLabel(lf, 'Anteile am Gesamtobjekt', 5, 0, 'nswe', 'w', (0,padx), pady)

        MyLabel(lf, 'IBAN der WEG ', 0, 1, 'nswe', 'w', padx, pady)
        te = TextEntry(lf, 1, 1,'nswe', (0,padx), pady )
        te.grid(columnspan=5)
        self._teIbanWEG = te

    def _createAusstattungFrame(self, row, padx, pady):
        lf = ttk.Labelframe(self, text='Ausstattung der Wohnung')
        lf.grid(column=0, row=row, sticky='nswe', padx=padx, pady=pady)
        cb = ttk.Checkbutton(lf, text='Balkon', variable=self._ivarBalkon)
        cb.grid(column=0, row=0, sticky='nswe', padx=padx, pady=pady)
        self._cbBalkon = cb

    def _createZubehoerFrame(self, row, padx, pady):
        pass

    def _createBemerkung(self, row, padx, pady):
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

