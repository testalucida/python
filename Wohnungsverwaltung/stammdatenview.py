from tkinter import *
from tkinter import ttk
from collections import UserDict

import sys
sys.path.append('/home/martin/Projects/python/mywidgets')
try:
    from mywidgets import TextEntry, FloatEntry, MyLabel, MyCombobox
    from interfaces import XWohnungDaten
    from editablegroup import EditSaveFunctionBar, EditableGroupAction
    from mycalendar import DateEntry
    import datehelper
    from buttonfactory import ButtonFactory
except ImportError:
    print("couldn't import my widgets.")

class StammdatenView(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self._teStrasse = None
        self._tePlz = None
        self._teOrt = None
        self._teWhg_bez = None
        self._deAngeschafft_am = None
        self._teEinhwert_az = None
        self._cboVermieter = None
        self._cboVerwalter = None
        self._isModified = False
        self._callback = None
        self._createUI()

    def _createUI(self):
        padx = pady = 5
        self.columnconfigure(1, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)

        MyLabel(self, 'Straße: ', 0, 0, 'nswe', 'e', padx, pady)
        self._teStrasse = TextEntry(self, 1, 0, 'nswe', padx, pady)
        self._teStrasse.setBackground('My.TEntry', 'lightyellow')
        self._teStrasse.setWidth(30)
        self._teStrasse.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'PLZ/Ort: ', 0, 1, 'nswe', 'e', padx, pady)
        f = ttk.Frame(self)
        f.columnconfigure(1, weight=1)
        self._tePlz = TextEntry(f, 0, 0, 'nsw', padx=(0, 3))
        self._tePlz['width'] = 6
        self._tePlz.setBackground('My.TEntry', 'lightyellow')
        self._tePlz.registerModifyCallback(self._onWohnungModified)

        self._teOrt = TextEntry(f, 1, 0, 'nswe')
        self._teOrt.setBackground('My.TEntry', 'lightyellow')
        self._teOrt.setWidth(30)
        self._teOrt.registerModifyCallback(self._onWohnungModified)
        f.grid(column=1, row=1, sticky='nswe', padx=padx, pady=pady)

        MyLabel(self, 'Whg.-Bez.: ', 0, 2, 'nswe', 'e', padx, pady)
        self._teWhg_bez = TextEntry(self, 1, 2, 'nswe', padx, pady)
        self._teWhg_bez.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'Angeschafft am: ', 0, 3, 'nswe', 'e', padx, pady)
        de = DateEntry(self)
        de.setUseCalendar(False)
        de['width'] = 10
        de.grid(column=1, row=3, sticky='nw', padx=padx, pady=pady)
        self._deAngeschafft_am = de
        self._deAngeschafft_am.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'Einhts.wert-Az: ', 0, 4, 'nswe', 'e', padx, pady)
        self._teEinhwert_az = TextEntry(self, 1, 4, 'nswe', padx, pady)
        #self._teEinhwert_az.grid(columnspan=2)
        self._teEinhwert_az.registerModifyCallback(self._onWohnungModified)

        MyLabel(self, 'Vermieter:', column=0, row=5, sticky='nse', anchor='e', padx=padx, pady=pady)
        cbo = MyCombobox(self)
        cbo.setItems(('Martin Kendel, Schellenberg', 'Gudrun Kendel, Schellenberg'))
        cbo.setReadonly(True)
        cbo.registerModifyCallback(self._onVermieterChanged)
        cbo.grid(column=1, row=5, sticky='we', padx=padx, pady=pady)
        self._cboVermieter = cbo

        btn = ButtonFactory.getNewButton(self, 'Neuen Vermieter anlegen', self._onNewVermieter)
        btn.grid(column=2, row=5, sticky='swe', padx=(0, 0), pady=pady)
        btnEdit = ButtonFactory.getEditButton(self, 'Vermieterdaten ändern', self._onEditVermieter)
        btnEdit.grid(column=3, row=5, sticky='swe', padx=(0,0), pady=pady)

        MyLabel(self, 'Verwalter:', column=0, row=6, sticky='nse', padx=padx, pady=pady)
        cbo = MyCombobox(self)
        cbo.setItems(('Hugo Baldrian, Nürnberg', 'Susanne Schleimich, Fürth'))
        cbo.setReadonly(True)
        cbo.registerModifyCallback(self._onVerwalterChanged)
        cbo.grid(column=1, row=6, sticky='we', padx=padx, pady=pady)
        self._cboVerwalter = cbo

        btn2 = ButtonFactory.getNewButton(self, 'Neuen Verwalter anlegen', self._onNewVerwalter)
        btn2.grid(column=2, row=6, sticky='swe', padx=(0,0), pady=pady)
        btnEdit2 = ButtonFactory.getEditButton(self, 'Vermieterdaten ändern', self._onEditVerwalter)
        btnEdit2.grid(column=3, row=6, sticky='swe', padx=(0, 0), pady=pady)

    def _onWohnungModified(self, widget: Widget, name: str, index: str, mode: str):
        self._isModified = True
        if self._callback:
            self._callback()

    def _onVermieterChanged(self, widget: Widget, name: str, index: str, mode: str):
        print('onVermieterChanged')

    def _onVerwalterChanged(self, widget: Widget, name: str, index: str, mode: str):
        print('onVerwalterChanged')

    def _onNewVermieter(self, arg):
        print('onNewVermieter')

    def _onEditVermieter(self, arg):
        print('onEditVermieter')

    def _onNewVerwalter(self, arg):
        print('onNewVerwalter')

    def _onEditVerwalter(self, arg):
        print('onEditVerwalter')

    def registerModifyCallback(self, callback) -> None:
        self._callback = callback

    def isModified(self) -> bool:
        return self._isModified

    def setData(self, data: XWohnungDaten) -> None:
        self._teStrasse = data.strasse
        self._tePlz = data.plz
        self._teOrt = data.ort
        self._teWhg_bez = data.whg_bez
        self._deAngeschafft_am = data.angeschafft_am
        self._teEinhwert_az = data.einhwert_az
        self._cboVermieter.setItems(data.vermieter_list)
        self._cboVermieter.setIndex(data.vermieter)
        self._cboVerwalter.setItems(data.verwalter_list)
        self._cboVerwalter.setIndex(data.verwalter)
        self._isModified = False

    def getData(self) -> XWohnungDaten:
        d: XWohnungDaten = XWohnungDaten()
        d.strasse = self._teStrasse.getValue()
        d.plz = self._tePlz.getValue()
        d.ort = self._teOrt.getValue()
        d.whg_bez = self._teWhg_bez.getValue()
        d.angeschafft_am = self._deAngeschafft_am.getValue()
        d.einhwert_az = self._teEinhwert_az.getValue()
        d.verwalter = self._cboVerwalter.getCurrentIndex()
        d.vermieter = self._cboVermieter.getCurrentIndex()
        d.verwalter_list = self._cboVerwalter.getItems()
        d.vermieter_list = self._cboVermieter.getItems()
        return d

    def clearData(self):
        self._teStrasse.clear()
        self._teWhg_bez.clear()
        self._tePlz.clear()
        self._teOrt.clear()
        self._teEinhwert_az.clear()
        self._deAngeschafft_am.clear()

class StammdatenView__alt(ttk.Frame):
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

    def kannweg(self, action: EditableGroupAction):
        print(action)

    def _createVermieterLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Vermieterstammdaten')
        lf.columnconfigure(1, weight=1)
        #lf.columnconfigure(3, weight=1)
        lf.columnconfigure(4, weight=1)
        lf.columnconfigure(5, weight=1)

        row = 0
        MyLabel(lf, 'Vorname: ', 0, row, 'nswe', 'e', padx, pady)
        self._vorname = TextEntry(lf, 1, row, 'nswe', padx, pady)
        self._vorname.setBackground('My.TEntry', 'lightyellow')
        self._vorname.registerModifyCallback(self._onVermieterModified)

        MyLabel(lf, 'Name: ', 2, row, 'nswe', 'e', padx, pady)
        self._name = TextEntry(lf, 3, row, 'nswe', padx, pady)
        self._name.setBackground('My.TEntry', 'lightyellow')
        self._name.grid(columnspan=2)
        self._name.registerModifyCallback(self._onVermieterModified)

        row += 1
        MyLabel(lf, 'Straße: ', 0, row, 'nswe', 'e', padx, pady)
        self._strasse = TextEntry(lf, 1, row, 'nswe', padx, pady)
        self._strasse.registerModifyCallback(self._onVermieterModified)

        l = MyLabel(lf, 'PLZ/Ort: ', 2, row, 'nswe', 'e', padx, pady)
        self._plz = TextEntry(lf, 3, row, 'nsw', padx, pady)
        self._plz['width'] = 6
        self._plz.registerModifyCallback(self._onVermieterModified)

        #MyLabel(lf, 'Ort: ', 4, 1, 'nswe', 'e', padx, pady)
        self._ort = TextEntry(lf, 4, row, 'nswe', padx, pady)
        self._ort.registerModifyCallback(self._onVermieterModified)

        row += 1
        l = MyLabel(lf, 'Steuernummer: ', 0, row, 'nswe', 'e', padx, pady)
        self._steuernummer = TextEntry(lf, 1, row, 'nswe', padx, pady)
        self._steuernummer.setBackground('My.TEntry', 'lightyellow')
        self._steuernummer.registerModifyCallback(self._onVermieterModified)

        funcbar = EditSaveFunctionBar(lf, self.kannweg)
        funcbar.grid(column=4, row=row, sticky='e')

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

        funcbar = EditSaveFunctionBar(lf, self.kannweg)
        funcbar.grid(column=4, row=3, sticky='e')

        return lf

    def _createVerwalterLabelframe(self, padx: int, pady: int) -> ttk.Labelframe:
        lf = ttk.Labelframe(self, text='Verwalterstammdaten')
        lf.columnconfigure(1, weight=1)
        #lf.columnconfigure(3, weight=1)
        #lf.columnconfigure(4, weight=1)
        #lf.columnconfigure(5, weight=1)

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

        funcbar = EditSaveFunctionBar(lf, self.kannweg)
        funcbar.grid(column=4, row=3, sticky='e')

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
