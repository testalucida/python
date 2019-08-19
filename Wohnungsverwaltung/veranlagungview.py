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
        self._vj_combo = None
        self._art_afa = None
        self._prozent_afa = None
        self._betrag_afa = None
        self._afa_wie_vj = None

        self._isAfaInitialized = False
        self._isAfaModified = False

        self._vjChange_callback = None

        self._createGui()

    def isAfaModified(self) -> bool:
        return self._isAfaModified

    def registerVjChangeCallback(self, cbfnc):
        self._vjChange_callback = cbfnc

    def _onVjSelectionChanged(self, evt):
        if self._vjChange_callback:
            self._vjChange_callback(self._vj_combo.getValue())

    def _onAfaModified(self, widget: Widget, name: str, index: str, mode: str):
        if self._isAfaInitialized:
            self._isAfaModified = True

    def _createGui(self):
        padx=pady=5
        #self.columnconfigure(0, weight=1)

        self._whg_short = self._createWohnungShort(self, padx, pady)
        self._whg_short.grid(column=0, row=0, sticky='nswe')

        f = self._createVjFrame(self, padx, pady)
        f.grid(column=0, row=1, sticky='nswe')

        lf = self._createAfaLabelframe(padx, pady)
        lf.grid(column=0, row=2, sticky='nswe', pady=(15, pady))

        f = self._createButtonFrame(self, padx, pady)
        f.grid(column=0, row=3)

    def _createWohnungShort(self, parent, padx, pady) -> ttk.Label:
        lbl = MyLabel(parent, text='Nürnberg, XStraße 22, Whg. 334', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady)
        lbl.setBackground('whg_short.TLabel', 'gray')
        lbl.setForeground('whg_short.TLabel', 'white')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('whg_short.TLabel', 10, 10)

        # lbl = ttk.Label(parent, text='Nürnberg, XStraße 22, Whg 334',
        #                 anchor='center', relief='sunken')
        # style = ttk.Style()
        # style.configure('whg_short.TLabel', background='gray', foreground='white',
        #                 font='Helvetica 16 bold', padding=(10))
        # lbl['style'] = 'whg_short.TLabel'
        return lbl

    def _createVjFrame(self, parent, padx, pady) -> MyCombobox:
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
        c.grid(column=2, row=0, sticky='w', pady=pady)
        c.bind('<<ComboboxSelected>>', self._onVjSelectionChanged)
        self._vj_combo = c

        return f

    def _createAfaLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='AfA-Daten')
        #lf.columnconfigure(1, weight=1)

        MyLabel(lf, 'Art der Absetzung: ', 0, 1, 'nswe', 'e', padx, pady)
        cb = MyCombobox(lf)
        cb.setBackground('AfA.TCombobox', 'lightyellow')
        cb.setItems(('', 'linear', 'degressiv'))
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
        f.setBackground('AfA.TEntry', 'lightyellow')
        f.grid(column=1, row=2, sticky='w', padx=padx, pady=pady)
        f.setWidth(8)
        self._betrag_afa = f

        MyLabel(lf, 'Wie Vorjahr: ', 2, 2, 'nswe', 'e', padx, pady)
        c = MyCombobox(lf)
        #c.setBackground('AfA.TCombobox', 'red')
        c.setStyle('AfA.TCombobox')
        c.setItems(('', 'Ja', 'Nein'))
        c.setIndex(0)
        c.setWidth(4)
        c.grid(column=3, row=2, sticky='w', padx=padx, pady=pady)
        self._afa_wie_vj = c

        return lf

    def _createButtonFrame(self, parent, padx: int, pady: int) -> ttk.Frame:
        f = ttk.Frame(parent)
        btn = ttk.Button(f, text='Speichern')
        btn['state'] = 'disabled'
        btn.grid(column=0, row=0, pady=pady)

        btn = ttk.Button(f, text='Anlage V erstellen')
        btn.grid(column=1, row=0, pady=pady)
        return f

    def clear(self):
        self._art_afa.clear()
        self._prozent_afa.clear()
        self._afa_wie_vj.clear()
        self._betrag_afa.clear()

    def setAfaData(self, data: dict) -> None:
        self._art_afa.setValue(data['art_afa'])
        self._prozent_afa.setValue(data['prozent'])
        self._afa_wie_vj.setValue(data['afa_wie_vorjahr'])
        self._betrag_afa.setValue(data['betrag'])

    def setWohungData(self, data: dict) -> None:
        s = ''.join((data['ort'], ', ', data['strasse'], ', ', data['whg_bez']))
        self._whg_short['text'] = s

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
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
