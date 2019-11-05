from tkinter import *
from tkinter import ttk
import sys
sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from mywidgets import TextEntry, FloatEntry, IntEntry, MyLabel, MyCombobox
    from mycalendar import DateEntry
    import datehelper
except ImportError:
    print("couldn't import my widgets.")

class VeranlagungView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._whg_ident = None
        self._angeschafft_am = None
        self._einhwert_az = None
        self._zurechng_ehemann = None
        self._zurechng_ehefrau = None
        self._vj_combo = None
        self._art_afa = None
        self._prozent_afa = None
        self._betrag_afa = None
        self._afa_wie_vj = None
        #self._verwaltkosten = None
        #self._sonstigeKosten = None
        self._btnSave = None
        self._btnCreateAnlageV = None

        self._isAfaInitialized = False
        self._isAfaModified = False

        self._isWhgInitialized = False
        self._isWhgModified = False

        self._vjChange_callback = None
        self._save_callback = None
        self._createAnlageV_callback = None

        self._createGui()

    def isAfaModified(self) -> bool:
        return self._isAfaModified

    def isWhgModified(self) -> bool:
        return self._isWhgModified

    def registerVjChangeCallback(self, cbfnc):
        self._vjChange_callback = cbfnc

    def registerSaveCallback(self, cbfnc):
        self._save_callback = cbfnc

    def registerCreateAnlageVCallback(self, cbfnc):
        self._createAnlageV_callback = cbfnc

    def _onVjSelectionChanged(self, evt):
        if self._vjChange_callback:
            self._vjChange_callback(self._vj_combo.getValue())

    def _onAfaModified(self, widget: Widget, name: str, index: str, mode: str):
        if self._isAfaInitialized:
            #print("VeranlagungView._onAfaModified: setting _isAfaModified = True")
            self._isAfaModified = True
            self.setSaveButtonEnabled(True)
            self.setCreateAnlageVButtonEnabled(False)

    def _onWhgModified(self, widget: Widget, name: str, index: str, mode: str):
        if self._isWhgInitialized:
            #print('VeranlagungView._onWhgModified')
            self._isWhgModified = True
            self.setSaveButtonEnabled(True)
            self.setCreateAnlageVButtonEnabled(False)

    def _onSavePressed(self):
        #print("Veranlagungsview._onSavePressed: _isAfaModified == ", self._isAfaModified)
        self.setSaveButtonEnabled(False)
        if self._save_callback:
            self._save_callback(self.getVeranlagData())
        self._isWhgModified = False
        self._isAfaModified = False

    def _onCreateAnlageVPressed(self):
        if self._createAnlageV_callback:
            self._createAnlageV_callback(self.getVeranlagData())

    def _createGui(self):
        padx=pady=5
        #self.columnconfigure(0, weight=1)

        self._whg_ident = self._createWohnungIdent(self, padx, pady)
        self._whg_ident.grid(column=0, row=0, sticky='nswe')

        f = self._createWohnungLabelFrame(padx, pady)
        f.grid(column=0, row=1, sticky='nswe', padx=padx, pady=(20,20))

        f = self._createVjFrame(self, padx, pady)
        f.grid(column=0, row=2, sticky='nswe')

        lf = self._createAfaLabelframe(padx, pady)
        lf.grid(column=0, row=3, sticky='nswe', pady=(10, pady))

        # lf = self._createWerbungskostenLabelframe(padx, pady)
        # lf.grid(column=0, row=4, sticky='nswe', pady=(40, 20))

        f = self._createButtonFrame(self, padx, pady=(15,5))
        f.grid(column=0, row=5)

    def _createWohnungIdent(self, parent, padx, pady) -> ttk.Label:
        lbl = MyLabel(parent, text='', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady)
        lbl.setBackground('whg_short.TLabel', 'gray')
        lbl.setForeground('whg_short.TLabel', 'white')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('whg_short.TLabel', 10, 10)
        return lbl

    def _createVjFrame(self, parent, padx, pady) -> ttk.Frame:
        f = ttk.Frame(parent)
        f.columnconfigure(0, weight=1)
        f.columnconfigure(3, weight=2)
        #
        l = MyLabel(f, 'Veranlagungsjahr', 1, 0, 'w', 'w', padx, pady)
        l.setWidth(16)

        c = MyCombobox(f)
        c.setTextPadding('Vj.TCombobox', 5, 5, 0)
        c.setWidth(5)
        c.setFont('Helvetica 16 bold')
        yearlist = datehelper.getLastYears(3)
        yearlist.insert(0, '')
        c.setItems(yearlist)
        c.setIndex(0)
        c.setReadonly(True)
        c.registerModifyCallback(self._onAfaModified)
        c.grid(column=2, row=0, sticky='w', pady=pady)
        c.bind('<<ComboboxSelected>>', self._onVjSelectionChanged)
        self._vj_combo = c

        return f

    def _createWohnungLabelFrame(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Wohnung')
        lbl = MyLabel(lf, 'Angeschafft am: ', 0, 0, 'nsw', 'w', padx, pady)
        de = DateEntry(lf)
        de.setBackground('Whg.TEntry', 'lightyellow')
        de.setUseCalendar(False)
        de['width'] = 10
        de.registerModifyCallback(self._onWhgModified)
        de.grid(column=1,row=0, sticky = 'nsw', padx=padx, pady=pady)
        self._angeschafft_am = de

        MyLabel(lf, 'Einh.wert-Az: ', 2, 0, 'nswe', 'e', padx, pady)
        te = TextEntry(lf, 3, 0, 'nsw', padx, pady)
        te.grid_configure(columnspan=2)
        te.setBackground('Whg.TEntry', 'lightyellow')
        te.registerModifyCallback(self._onWhgModified)
        self._einhwert_az = te

        lbl = MyLabel(lf, 'Steuerl. Überschuss/Verlust zurechnen auf Ehemann/Ehefrau (%):',
                      0, 1, 'nsw', 'w', padx, pady)
        lbl.grid_configure(columnspan=3)

        self._zurechng_ehemann = IntEntry(lf)
        ie = self._zurechng_ehemann
        ie.grid(column=3, row=1, sticky='nse', padx=padx, pady=pady)
        ie.setWidth(4)
        ie.setBackground('Whg.TEntry', 'lightyellow')
        ie.setValue(100)
        ie.registerModifyCallback(self._onWhgModified)

        self._zurechng_ehefrau = IntEntry(lf)
        ie2 = self._zurechng_ehefrau
        ie2.grid(column=4, row=1, sticky='nsw', padx=padx, pady=pady)
        ie2.setWidth(4)
        ie2.setBackground('Whg.TEntry', 'lightyellow')
        ie2.setValue(0)
        ie2.registerModifyCallback(self._onWhgModified)

        return lf

    def _createAfaLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='AfA')
        #lf.columnconfigure(1, weight=1)

        MyLabel(lf, 'Art der Absetzung: ', 0, 1, 'nswe', 'e', padx, pady)
        cb = MyCombobox(lf)
        cb.setBackground('AfA.TCombobox', 'lightyellow')
        cb.setItems(('', 'linear', 'degressiv'))
        cb.setIndex(0)
        cb.setReadonly(True)
        cb.registerModifyCallback(self._onAfaModified)
        cb.grid(column=1, row=1, sticky='w', padx=padx, pady=pady)
        self._art_afa = cb

        MyLabel(lf, 'Prozentsatz:  ', 2, 1, 'nswe', 'e', padx, pady)
        f = FloatEntry(lf)
        f.grid(column=3, row=1, sticky='w', padx=padx, pady=pady)
        f['width'] = 4
        f.registerModifyCallback(self._onAfaModified)
        self._prozent_afa = f

        MyLabel(lf, 'Betrag: ', 0, 2, 'nswe', 'e', padx, pady)
        f = IntEntry(lf)
        f.setBackground('AfA.TEntry', 'lightyellow')
        f.grid(column=1, row=2, sticky='w', padx=padx, pady=pady)
        f.setWidth(8)
        f.registerModifyCallback(self._onAfaModified)
        self._betrag_afa = f

        MyLabel(lf, 'Wie Vorjahr: ', 2, 2, 'nswe', 'e', padx, pady)
        c = MyCombobox(lf)
        #c.setBackground('AfA.TCombobox', 'red')
        c.setStyle('AfA.TCombobox')
        c.setItems(('', 'Ja', 'Nein'))
        c.setIndex(0)
        c.setWidth(4)
        c.setReadonly(True)
        c.registerModifyCallback(self._onAfaModified)
        c.grid(column=3, row=2, sticky='w', padx=padx, pady=pady)
        self._afa_wie_vj = c

        return lf

    def _createWerbungskostenLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self,
                            text='Verwaltung gem. Anlage V Zeile 47')

        # MyLabel(lf,
        #         'Verwaltungskosten inkl. Bankspesen '
        #         'gem. Betriebskostenabrechnung: ',
        #         0, 0, 'nswe', 'e', padx, pady)
        # f = IntEntry(lf)
        # f.setBackground('AfA.TEntry', 'lightyellow')
        # f.grid(column=1, row=0, sticky='w', padx=padx, pady=pady)
        # f['width'] = 5
        # f.registerModifyCallback(self._onAfaModified)
        # self._verwaltkosten = f

        # MyLabel(lf, 'Sonstige Kosten (Fahrten, Tel., '
        #             'allg. Rep. gem. Betriebskostenabrechnung): ', 0, 1,
        #         'nswe', 'e', padx, pady)
        # f = IntEntry(lf)
        # f.grid(column=1, row=1, sticky='w', padx=padx, pady=pady)
        # f.setWidth(5)
        # f.registerModifyCallback(self._onAfaModified)
        # self._sonstigeKosten = f

        return lf

    def _createButtonFrame(self, parent, padx: int, pady: int) -> ttk.Frame:
        f = ttk.Frame(parent)
        btn = ttk.Button(f, text='Speichern', command=self._onSavePressed)
        btn.grid(column=0, row=0, pady=pady)
        self._btnSave = btn

        btn = ttk.Button(f, text='Anlage V erstellen',
                         command=self._onCreateAnlageVPressed)
        btn.grid(column=1, row=0, pady=pady)
        self._btnCreateAnlageV = btn
        return f

    def clearAll(self):
        self.clearAfa()
        self.clearWohnung()

    def clearWohnung(self):
        self._isWhgInitialized = False
        self._isWhgModified = False
        self._angeschafft_am.clear()
        self._einhwert_az.clear()
        self._zurechng_ehefrau.clear()
        self._zurechng_ehemann.clear()

    def clearAfa(self):
        self._isAfaInitialized = False
        self._isAfaModified = False
        self._art_afa.clear()
        self._prozent_afa.clear()
        self._afa_wie_vj.clear()
        self._betrag_afa.clear()
        #self._verwaltkosten.clear()

    def setAfaData(self, data: dict) -> None:
        if data:
            self._isAfaInitialized = False
            self._art_afa.setValue(data['art_afa'])
            self._prozent_afa.setValue(data['prozent'])
            self._afa_wie_vj.setValue(data['afa_wie_vorjahr'])
            self._betrag_afa.setValue(data['betrag'])
            #self._verwaltkosten.setValue(data['verwaltkosten'])
        self._isAfaInitialized = True
        self._isAfaModified = False

    def setWohnungIdent(self, wohnungIdent: str):
        self._whg_ident.setValue(wohnungIdent)

    def getAfaAndVw(self) -> dict:
        return \
        {
            'vj_ab': self._vj_combo.getValue(),
            'art_afa': self._art_afa.getValue(),
            'prozent': self._prozent_afa.getValue(),
            'afa_wie_vorjahr': self._afa_wie_vj.getValue(),
            'betrag': self._betrag_afa.getValue()
        }

    def getVeranlagData(self) -> dict:
        """
        :return: Wohnung and AfA Data and Verwaltungskosten
        """
        a = self.getAfaAndVw()
        w = self.getWohnungData()
        for k, v in w.items():
            a[k] = v
        return a

    def setWohnungData(self, angeschafftAm: str, einhwertAz: str,
                      steuerl_zurechng_mann: int,
                      steuerl_zurechng_frau: int) -> None:
        self._isWhgInitialized = False
        self._angeschafft_am.setValue(angeschafftAm)
        self._einhwert_az.setValue(einhwertAz)
        self._zurechng_ehefrau.setValue(steuerl_zurechng_frau)
        self._zurechng_ehemann.setValue(steuerl_zurechng_mann)
        self._isWhgInitialized = True
        self._isWhgModified = False

    def getWohnungData(self) -> dict:
        return \
        {
            'angeschafft_am': self._angeschafft_am.getValue(),
            'einhwert_az': self._einhwert_az.getValue(),
            'steuerl_zurechng_mann': self._zurechng_ehemann.getValue(),
            'steuerl_zurechng_frau': self._zurechng_ehefrau.getValue()
        }

    def setSaveButtonEnabled(self, enabled: bool):
        self._btnSave['state'] = 'normal' if enabled else 'disabled'

    def setCreateAnlageVButtonEnabled(self, enabled: bool):
        self._btnCreateAnlageV['state'] = 'normal' if enabled else 'disabled'

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('test')
    root = Tk()
    # root.rowconfigure(0, weight=1)
    # root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    stv = VeranlagungView(root)
    stv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    test()
