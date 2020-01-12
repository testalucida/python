#import libs
from libs import *
from mietverhaeltnisview import MietverhaeltnisView
from business import DataProvider, WvException
from interfaces import XMietverhaeltnis, XMietverhaeltnisList

class MietverhaeltnisController:
    def __init__(self, dataprovider: DataProvider,
                 view: MietverhaeltnisView):
        self._dataProvider = dataprovider
        self._view: MietverhaeltnisView = view
        self._mietverhaeltnisse: XMietverhaeltnisList = None
        self._listIdx = 0  # Index des Mietverhältnisses in der Liste,
                           # der gerade angezeigt wird
        self._whg_id: int = -1

    def startWork(self) -> None:
        self._view.registerSaveCallback(self._onSave)
        self._view.registerNewMieterCallback(self._onNewMieter)
        self._view.registerPreviousNextMieterCallback(self._onPreviousNextMieter)

    def _onNewMieter(self, data: XMietverhaeltnis) -> None:
        self._view.clear()
        mv = XMietverhaeltnis()
        mv.whg_id = self._whg_id
        self._mietverhaeltnisse.append(mv)
        self._listIdx = self._mietverhaeltnisse.len() - 1
        self._view.setData(self._mietverhaeltnisse.getList()[self._listIdx])

    def _onPreviousNextMieter(self, data: XMietverhaeltnis, prevOrNext: int) -> None:
        '''
        reads previous or next mieter
        :param data: data of currently shown mieter
        :param prevOrNext: +1: previous mieter
                           -1: next mieter
        :return: None
        '''
        if not self._mietverhaeltnisse or \
                self._mietverhaeltnisse.len() == 0 or \
                self._listIdx + prevOrNext < 0 or \
                self._listIdx + prevOrNext >= self._mietverhaeltnisse.len():
            messagebox.showerror("Nicht unterstützte Aktion", "Blättern nicht möglich")
            return

        self._listIdx += prevOrNext
        self._view.setData(self._mietverhaeltnisse.getList()[self._listIdx])

    def _onSave(self, data: XMietverhaeltnis) -> None:
        msg = self._validate(data)
        if msg:
            messagebox.showerror('Falsche Eingabe', msg)
            return

        try:
            if data.mv_id <= 0:
                data.mv_id = self._dataProvider.insertMietverhaeltnis(data)
            else:
                self._dataProvider.updateMietverhaeltnis(data)
        except WvException as ex:
            messagebox.showerror("Speichern fehlgeschlagen", ex.message())
        except Exception as x:
            msg = type(x).__name__ + " in MietverhaeltnisController._onSave:\n" + \
                   x.args[0]
            messagebox.showerror("Speichern fehlgeschlagen", msg)

    def _validate(self, data: XMietverhaeltnis) -> str or None:
        if not data.anrede: return "Anrede fehlt."
        if not data.name: return "Name fehlt."
        if not data.vorname: return "Vorname fehlt."
        if not data.geboren_am: return "Geburtsdatum fehlt (für Kautionskonto)."
        if not data.vermietet_ab: return "Mietbeginn fehlt."
        return None

    def _loadData(self) -> None:
        try:
            mietverhaeltnisse: XMietverhaeltnisList = \
                self._dataProvider.getMietverhaeltnisse(self._whg_id)
            self._mietverhaeltnisse = mietverhaeltnisse
            self._view.setData(mietverhaeltnisse.getList()[self._listIdx])

        except WvException as ex:
            messagebox.showerror("Uuuups!", ex.message())

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadData()

    def clear(self):
        # called by wvcontroller: clear view and all member variables
        self._view.clear()
        self._whg_id = -1
        self._listIdx = 0
        self._mietverhaeltnisse = None


def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('test')
    root = Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    style = ttk.Style()
    style.theme_use('clam')

    v = MietverhaeltnisView(root)
    v.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)

    ctrl = MietverhaeltnisController(dp, v)
    ctrl.startWork()
    ctrl.wohnungSelected(10)

    root.mainloop()

if __name__ == '__main__':
    test()
