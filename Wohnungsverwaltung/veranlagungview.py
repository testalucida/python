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

class VeranlagungView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._whg_short = None
        self._vj = None
        self._art_afa = None
        self._prozent_afa = None
        self._betrag_afa = None
        self._afa_wie_vj = None

        self._isAfaInitialized = False
        self._isAfaModified = False

        self._createGui()
        self.columnconfigure(0, weight=1)

    def isAfaModified(self) -> bool:
        return self._isAfaModified

    def _onAfaModified(self, widget: Widget, name: str, index: str, mode: str):
        if self._isAfaInitialized:
            self._isAfaModified = True

    def _createGui(self):
        padx=pady=5

        lbl = MyLabel(self, text='Da guck', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady )
        lbl.setBackground('lightgray')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('WhgShort.TLabel', 10, 20)
        self._whg_short = lbl

        lf = self._createAfaLabelframe(padx, pady)
        lf.grid(column=0, row=3, sticky='nswe', pady=(15, pady))

        btn = ttk.Button(self, text='Speichern')
        btn['state'] = 'disabled'
        btn.grid(column=0, row=4, sticky='nswe', pady=pady)

    def _createAfaLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='AfA-Daten')
        #lf.columnconfigure(1, weight=1)

        f = self._createVjFrame(lf, padx, pady)
        f.grid(column=0, row=0, columnspan=3, pady=pady, stick='nswe')

        MyLabel(lf, 'Art der Absetzung: ', 0, 1, 'nswe', 'e', padx, pady)
        cb = MyCombobox(lf)
        cb.setBackground('AfA.TCombobox', 'lightyellow')
        cb.setItems(('linear', 'degressiv'))
        cb.setIndex(0)
        cb.grid(column=1, row=1, sticky='w', padx=padx, pady=pady)
        self._art_afa = cb

        MyLabel(lf, 'Prozentsatz:  ', 2, 1, 'nswe', 'e', padx, pady)
        f = FloatEntry(lf)
        f.grid(column=3, row=1, sticky='w', padx=padx, pady=pady)
        f['width'] = 4
        self._prozent_afa = f

        MyLabel(lf, 'Betrag: ', 0, 2, 'nswe', 'e', padx, pady)
        f = FloatEntry(lf)
        f.setBackground('My.TEntry', 'lightyellow')
        f.grid(column=1, row=2, sticky='w', padx=padx, pady=pady)
        f.setWidth(8)
        self._betrag_afa = f

        MyLabel(lf, 'Wie Vorjahr: ', 2, 2, 'nswe', 'e', padx, pady)
        c = MyCombobox(lf)
        c.setBackground('AfA.TCombobox', 'lightyellow')
        c.setItems(('Ja', 'Nein'))
        c.setIndex(0)
        c.setWidth(4)
        c.grid(column=3, row=2, sticky='w', padx=padx, pady=pady)
        self._afa_wie_vj = c

        return lf

    def _createVjFrame(self, parent, padx, pady) -> MyCombobox:
        f = ttk.Frame(parent)
        l = MyLabel(f, 'Veranlagungsjahr ', 0, 0, 'nswe', 'e', padx, pady)
        l.setWidth(30)

        c = MyCombobox(f)
        c.setTextPadding('My.TCombobox', 5, 5, 0)
        c.setWidth(5)
        c.setFont('Helvetica 16 bold')
        c.setItems(datehelper.getLastYears(3))
        c.setIndex(1)
        c.setReadonly(True)
        c.grid(column=1, row=0, pady=pady)
        self._vj = c
        return f

    def setAfaData(self, data: dict) -> None:
        pass

    def setWohungData(self, data: dict) -> None:
        s = ''.join((data['ort'], ', ', data['strasse'], ', ', data['whg_bez']))
        self._whg_short['text'] = s

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    stv = VeranlagungView(root)
    stv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    # ctrl = GrundsteuerController(dp, tv)
    # ctrl.startWork()
    # ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()
