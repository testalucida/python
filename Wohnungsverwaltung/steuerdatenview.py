from tkinter import *
from tkinter import ttk
import sys
sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from mywidgets import TextEntry, FloatEntry, MyLabel, MyCombobox
    from mycalendar import DateEntry
    import datehelper
except ImportError:
    print("couldn't import my widgets.")

class SteuerdatenView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._vj = None
        self._name = None
        self._vorname = None
        self._strasse = None
        self._plz = None
        self._ort = None
        self._steuernummer = None
        self._whg_strasse = None
        self._whg_bez = None
        self._whg_plz = None
        self._whg_ort = None
        self._einhwert_az = None
        self._angeschafft_am = None
        self._art_afa = None
        self._prozent_afa = None
        self._betrag_afa = None
        self._afa_wie_vj = None

        self._createGui()
        self.columnconfigure(0, weight=1)

    def _onKey(self, evt: Event):
        print(evt)

    def _createGui(self):
        padx=pady=5

        f = self._createVjFrame(padx, pady)
        f.grid(column=0, row=0, pady=pady, stick='nswe')

        lf = self._createVermieterLabelframe(padx, pady)
        lf.grid(column=0, row=1, sticky='nswe', pady=(15, pady))

        lf = self._createWohnungLabelframe(padx, pady)
        lf.grid(column=0, row=2, sticky='nswe', pady=(10,pady))

        lf = self._createAfaLabelframe(padx, pady)
        lf.grid(column=0, row=3, sticky='nswe', pady=(15, pady))

        btn = ttk.Button(self, text='Speichern')
        btn['state'] = 'disabled'
        btn.grid(column=0, row=4, sticky='nswe', pady=pady)

    def _createVjFrame(self, padx, pady) -> MyCombobox:
        f = ttk.Frame(self)
        l = MyLabel(f, 'Veranlagungsjahr ', 0, 0, 'nswe', 'e', padx, pady)
        l.setWidth(30)

        c = MyCombobox(f)
        c.setTextPadding('My.TCombobox', 10, 10, 0)
        c.setWidth(5)
        c.setFont('Helvetica 20 bold')
        c.setItems(datehelper.getLastYears(3))
        c.setIndex(1)
        c.setReadonly(True)
        c.grid(column=1, row=0, pady=pady)
        self._vj = c
        return f

    def _createVermieterLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Vermieterstammdaten')
        lf.columnconfigure(1, weight=1)
        #lf.columnconfigure(3, weight=1)
        lf.columnconfigure(4, weight=1)
        lf.columnconfigure(5, weight=1)

        MyLabel(lf, 'Vorname: ', 0, 0, 'nswe', 'e', padx, pady)
        self._vorname = TextEntry(lf, 1, 0, 'nswe', padx, pady)
        self._vorname.setBackground('My.TEntry', 'lightyellow')
        self._vorname.bind('<Key>', self._onKey)

        MyLabel(lf, 'Name: ', 2, 0, 'nswe', 'e', padx, pady)
        self._name = TextEntry(lf, 3, 0, 'nswe', padx, pady)
        self._name.setBackground('My.TEntry', 'lightyellow')
        self._name.grid(columnspan=2)


        MyLabel(lf, 'Straße: ', 0, 1, 'nswe', 'e', padx, pady)
        self._strasse = TextEntry(lf, 1, 1, 'nswe', padx, pady)

        l = MyLabel(lf, 'PLZ/Ort: ', 2, 1, 'nswe', 'e', padx, pady)
        self._plz = TextEntry(lf, 3, 1, 'nsw', padx, pady)
        self._plz['width'] = 6

        #MyLabel(lf, 'Ort: ', 4, 1, 'nswe', 'e', padx, pady)
        self._ort = TextEntry(lf, 4, 1, 'nswe', padx, pady)

        l = MyLabel(lf, 'Steuernummer: ', 0, 2, 'nswe', 'e', padx, pady)
        self._steuernummer = TextEntry(lf, 1, 2, 'nswe', padx, pady)
        self._steuernummer.setBackground('My.TEntry', 'lightyellow')

        return lf

    def _createWohnungLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Wohnungsdaten')
        lf.columnconfigure(1, weight=1)
        #lf.columnconfigure(3, weight=1)
        lf.columnconfigure(4, weight=1)
        lf.columnconfigure(5, weight=1)

        MyLabel(lf, 'Straße: ', 0, 0, 'nswe', 'e', padx, pady)
        self._whg_strasse = TextEntry(lf, 1, 0, 'nswe', padx, pady)
        self._whg_strasse.setBackground('My.TEntry', 'lightyellow')

        MyLabel(lf, 'PLZ/Ort: ', 2, 0, 'nswe', 'e', padx, pady)
        self._whg_plz = TextEntry(lf, 3, 0, 'nsw', padx, pady)
        self._whg_plz['width'] = 6
        self._whg_plz.setBackground('My.TEntry', 'lightyellow')

        self._whg_ort = TextEntry(lf, 4, 0, 'nswe', padx, pady)
        self._whg_ort.setBackground('My.TEntry', 'lightyellow')

        MyLabel(lf, 'Etage: ', 0, 1, 'nswe', 'e', padx, pady)
        self._whg_bez = TextEntry(lf, 1, 1, 'nswe', padx, pady)

        MyLabel(lf, 'Angeschafft am: ', 0, 2, 'nswe', 'e', padx, pady)
        de = DateEntry(lf)
        de.setBackground('My.TEntry', 'lightyellow')
        de.setUseCalendar(False)
        de['width'] = 10
        de.grid(column=1, row=2, sticky='nw', padx=padx, pady=pady)
        self._angeschafft_am = de

        MyLabel(lf, 'Einhts.wert-Az: ', 0, 3, 'nswe', 'e', padx, pady)
        self._einhwert_az = TextEntry(lf, 1, 3, 'nswe', padx, pady)
        self._einhwert_az.setBackground('My.TEntry', 'lightyellow')

        return lf

    def _createAfaLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='AfA-Daten')
        #lf.columnconfigure(1, weight=1)

        MyLabel(lf, 'Art der Absetzung: ', 0, 0, 'nswe', 'e', padx, pady)
        cb = MyCombobox(lf)
        cb.setBackground('AfA.TCombobox', 'lightyellow')
        cb.setItems(('linear', 'degressiv'))
        cb.setIndex(0)
        cb.grid(column=1, row=0, sticky='w', padx=padx, pady=pady)
        self._art_afa = cb

        MyLabel(lf, 'Prozentsatz:  ', 2, 0, 'nswe', 'e', padx, pady)
        f = FloatEntry(lf)
        f.grid(column=3, row=0, sticky='w', padx=padx, pady=pady)
        f['width'] = 4
        self._prozent_afa = f

        MyLabel(lf, 'Betrag: ', 0, 1, 'nswe', 'e', padx, pady)
        f = FloatEntry(lf)
        f.setBackground('My.TEntry', 'lightyellow')
        f.grid(column=1, row=1, sticky='w', padx=padx, pady=pady)
        f.setWidth(8)
        self._betrag_afa = f

        MyLabel(lf, 'Wie Vorjahr: ', 2, 1, 'nswe', 'e', padx, pady)
        c = MyCombobox(lf)
        c.setBackground('AfA.TCombobox', 'lightyellow')
        c.setItems(('Ja', 'Nein'))
        c.setIndex(0)
        c.setWidth(4)
        c.grid(column=3, row=1, sticky='w', padx=padx, pady=pady)
        self._afa_wie_vj = c

        return lf

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    stv = SteuerdatenView(root)
    stv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    # ctrl = GrundsteuerController(dp, tv)
    # ctrl.startWork()
    # ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()
