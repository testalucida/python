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

class StammdatenView(ttk.Frame):
    def __init__(self, parent: ttk.Frame):
        ttk.Frame.__init__(self, parent)
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
        self._verwalter_firma = None
        self._verwalter_strasse = None
        self._verwalter_plz = None
        self._verwalter_ort = None
        self._verwalter_tel = None
        self._verwalter_email = None
        self._isVermieterInitialized = False
        self._isVermieterModified = False
        self._isWohnungInitialized = False
        self._isWohnungModified = False
        self._isVerwalterInitialized = False
        self._isVerwalterModified = False
        self._btnSave = None

        self._createGui()
        self.columnconfigure(0, weight=1)

    def isVermieterModified(self) -> bool:
        return self._isVermieterModified

    def isWohnungModified(self) -> bool:
        return self._isWohnungModified

    def isVerwalterModified(self) -> bool:
        return self._isVerwalterModified

    def _onVermieterModified(self, widget: Widget, name: str, index: str, mode: str):
        #print('onVermieterModified')
        if self._isVermieterInitialized:
            self._isVermieterModified = True
            self._btnSave['state'] = 'normal'

    def _onWohnungModified(self, widget: Widget, name: str, index: str, mode: str):
        #print('onWohnungModified')
        if self._isWohnungInitialized:
            self._isWohnungModified = True
            self._btnSave['state'] = 'normal'

    def _onVerwalterModified(self, widget: Widget, name: str, index: str, mode: str):
        #print('onVerwalterModified')
        if self._isVerwalterInitialized:
            self._isVerwalterModified = True
            self._btnSave['state'] = 'normal'

    def _createGui(self):
        padx=pady=5

        lf = self._createVermieterLabelframe(padx, pady)
        lf.grid(column=0, row=1, sticky='nswe', pady=(15, pady))

        lf = self._createWohnungLabelframe(padx, pady)
        lf.grid(column=0, row=2, sticky='nswe', pady=(10,pady))

        lf = self._createVerwalterLabelframe(padx, pady)
        lf.grid(column=0, row=3, sticky='nswe', pady=(10, pady))

        btn = ttk.Button(self, text='Speichern')
        btn['state'] = 'disabled'
        btn.grid(column=0, row=4, sticky='nswe', pady=pady)
        self._btnSave = btn

    def _createVermieterLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Vermieterstammdaten')
        lf.columnconfigure(1, weight=1)
        #lf.columnconfigure(3, weight=1)
        lf.columnconfigure(4, weight=1)
        lf.columnconfigure(5, weight=1)

        MyLabel(lf, 'Vorname: ', 0, 0, 'nswe', 'e', padx, pady)
        self._vorname = TextEntry(lf, 1, 0, 'nswe', padx, pady)
        self._vorname.setBackground('My.TEntry', 'lightyellow')
        self._vorname.registerModifyCallback(self._onVermieterModified)

        MyLabel(lf, 'Name: ', 2, 0, 'nswe', 'e', padx, pady)
        self._name = TextEntry(lf, 3, 0, 'nswe', padx, pady)
        self._name.setBackground('My.TEntry', 'lightyellow')
        self._name.grid(columnspan=2)
        self._name.registerModifyCallback(self._onVermieterModified)

        MyLabel(lf, 'Straße: ', 0, 1, 'nswe', 'e', padx, pady)
        self._strasse = TextEntry(lf, 1, 1, 'nswe', padx, pady)
        self._strasse.registerModifyCallback(self._onVermieterModified)

        l = MyLabel(lf, 'PLZ/Ort: ', 2, 1, 'nswe', 'e', padx, pady)
        self._plz = TextEntry(lf, 3, 1, 'nsw', padx, pady)
        self._plz['width'] = 6
        self._plz.registerModifyCallback(self._onVermieterModified)

        #MyLabel(lf, 'Ort: ', 4, 1, 'nswe', 'e', padx, pady)
        self._ort = TextEntry(lf, 4, 1, 'nswe', padx, pady)
        self._ort.registerModifyCallback(self._onVermieterModified)

        l = MyLabel(lf, 'Steuernummer: ', 0, 2, 'nswe', 'e', padx, pady)
        self._steuernummer = TextEntry(lf, 1, 2, 'nswe', padx, pady)
        self._steuernummer.setBackground('My.TEntry', 'lightyellow')
        self._steuernummer.registerModifyCallback(self._onVermieterModified)

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
        self._whg_strasse.registerModifyCallback(self._onWohnungModified)

        MyLabel(lf, 'PLZ/Ort: ', 2, 0, 'nswe', 'e', padx, pady)
        self._whg_plz = TextEntry(lf, 3, 0, 'nsw', padx, pady)
        self._whg_plz['width'] = 6
        self._whg_plz.setBackground('My.TEntry', 'lightyellow')
        self._whg_plz.registerModifyCallback(self._onWohnungModified)

        self._whg_ort = TextEntry(lf, 4, 0, 'nswe', padx, pady)
        self._whg_ort.setBackground('My.TEntry', 'lightyellow')
        self._whg_ort.registerModifyCallback(self._onWohnungModified)

        MyLabel(lf, 'Whg.-Bez.: ', 0, 1, 'nswe', 'e', padx, pady)
        self._whg_bez = TextEntry(lf, 1, 1, 'nswe', padx, pady)
        self._whg_bez.registerModifyCallback(self._onWohnungModified)

        MyLabel(lf, 'Angeschafft am: ', 0, 2, 'nswe', 'e', padx, pady)
        de = DateEntry(lf)
        de.setBackground('My.TEntry', 'lightyellow')
        de.setUseCalendar(False)
        de['width'] = 10
        de.grid(column=1, row=2, sticky='nw', padx=padx, pady=pady)
        self._angeschafft_am = de
        self._angeschafft_am.registerModifyCallback(self._onWohnungModified)

        MyLabel(lf, 'Einhts.wert-Az: ', 0, 3, 'nswe', 'e', padx, pady)
        self._einhwert_az = TextEntry(lf, 1, 3, 'nswe', padx, pady)
        self._einhwert_az.setBackground('My.TEntry', 'lightyellow')
        self._einhwert_az.registerModifyCallback(self._onWohnungModified)

        return lf

    def _createVerwalterLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Verwalterstammdaten')
        lf.columnconfigure(1, weight=1)
        #lf.columnconfigure(3, weight=1)
        lf.columnconfigure(4, weight=1)
        lf.columnconfigure(5, weight=1)

        MyLabel(lf, 'Firma: ', 0, 0, 'nswe', 'e', padx, pady)
        self._verwalter_firma = TextEntry(lf, 1, 0, 'nswe', padx, pady)
        self._verwalter_firma.grid(columnspan=4)
        self._verwalter_firma.registerModifyCallback(self._onVerwalterModified)

        MyLabel(lf, 'Straße: ', 0, 1, 'nswe', 'e', padx, pady)
        self._verwalter_strasse = TextEntry(lf, 1, 1, 'nswe', padx, pady)
        self._verwalter_strasse.registerModifyCallback(self._onVerwalterModified)

        l = MyLabel(lf, 'PLZ/Ort: ', 2, 1, 'nswe', 'e', padx, pady)
        self._verwalter_plz = TextEntry(lf, 3, 1, 'nsw', padx, pady)
        self._verwalter_plz['width'] = 6
        self._plz.registerModifyCallback(self._onVerwalterModified)

        self._verwalter_ort = TextEntry(lf, 4, 1, 'nswe', padx, pady)
        self._verwalter_ort.registerModifyCallback(self._onVerwalterModified)

        l = MyLabel(lf, 'Telefon: ', 0, 2, 'nswe', 'e', padx, pady)
        self._verwalter_tel = TextEntry(lf, 1, 2, 'nswe', padx, pady)
        self._verwalter_tel.registerModifyCallback(self._onVerwalterModified)

        l = MyLabel(lf, 'eMail: ', 2, 2, 'nswe', 'e', padx, pady)
        self._verwalter_email = TextEntry(lf, 3, 2, 'nswe', padx, pady)
        self._verwalter_email.grid(columnspan=2)
        self._verwalter_email.registerModifyCallback(self._onVerwalterModified)

        return lf

    def clear(self):
        self.clearWohnungData()
        self.clearVermieterData()
        self.clearVerwalterData()
        self.update()

    def clearWohnungData(self):
        self._whg_strasse.clear()
        self._whg_bez.clear()
        self._whg_plz.clear()
        self._whg_ort.clear()
        self._einhwert_az.clear()
        self._angeschafft_am.clear()
        self._isWohnungInitialized = False

    def clearVermieterData(self):
        self._vorname.clear()
        self._name.clear()
        self._strasse.clear()
        self._plz.clear()
        self._ort.clear()
        self._steuernummer.clear()
        self._isVermieterInitialized = False

    def clearVerwalterData(self):
        self._verwalter_firma.clear()
        self._verwalter_strasse.clear()
        self._verwalter_plz.clear()
        self._verwalter_ort.clear()
        self._verwalter_tel.clear()
        self._verwalter_email.clear()
        self._isVerwalterInitialized = False

    def setVermieterData(self, data: dict) -> None:
        self._vorname.setValue(data['vorname'])
        self._name.setValue(data['name'])
        self._strasse.setValue(data['strasse'])
        self._plz.setValue(data['plz'])
        self._ort.setValue(data['ort'])
        self._steuernummer.setValue(data['steuernummer'])
        self._isVermieterInitialized = True

    def setWohnungData(self, data: dict) -> None:
        self._whg_strasse.setValue(data['strasse'])
        self._whg_bez.setValue(data['whg_bez'])
        self._whg_plz.setValue(data['plz'])
        self._whg_ort.setValue(data['ort'])
        self._einhwert_az.setValue(data['einhwert_az'])
        self._angeschafft_am.setValue(data['angeschafft_am'])
        self._isWohnungInitialized = True

    def setVerwalterData(self, data: dict) -> None:
        self._verwalter_firma.setValue(data['firma'])
        self._verwalter_strasse.setValue(data['strasse'])
        self._verwalter_plz.setValue(data['plz'])
        self._verwalter_ort.setValue(data['ort'])
        self._verwalter_tel.setValue(data['telefon'])
        self._verwalter_email.setValue(data['email'])
        self._isVerwalterInitialized = True

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    stv = StammdatenView(root)
    stv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    # ctrl = GrundsteuerController(dp, tv)
    # ctrl.startWork()
    # ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()
