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

class WohnungView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
        self._lbl_ident = None
        self._cbo_zimmer = None
        self._ie_qm = None
        self._cb_ebk = None
        self._cb_balkon = None
        self._cb_tageslichtbad = None
        self._cb_dusche = None
        self._cb_wanne = None
        self._cb_bidet = None
        #self._txt_zusatz = None
        self._txt_heizung = None
        self._txt_bemerkung = None
        self._cb_kellerabteil = None
        self._cbo_garage = None
        self._cb_aufzug = None
        self._createUI()
        self.columnconfigure(0, weight=1)

    def _createUI(self):
        padx = pady = 5
        self._lbl_ident = self._createWohnungIdent(padx, pady)

    def _createWohnungIdent(self, padx, pady) -> ttk.Label:
        lbl = MyLabel(self, text='', column=0, row=0, sticky='nswe',
                      anchor='center', padx=padx, pady=pady)
        lbl.setBackground('whg_short.TLabel', 'gray')
        lbl.setForeground('whg_short.TLabel', 'white')
        lbl.setFont('Helvetica 14 bold')
        lbl['relief'] = 'sunken'
        lbl.setTextPadding('whg_short.TLabel', 10, 10)
        return lbl

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    wv = WohnungView(root)
    wv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    root.mainloop()

if __name__ == '__main__':
    test()

