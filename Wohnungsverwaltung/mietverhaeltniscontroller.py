#import libs
from libs import *
from mietverhaeltnisview import MietverhaeltnisView
from business import DataProvider, WvException
from interfaces import XMietverhaeltnis

class MietverhaeltnisController:
    def __init__(self, dataprovider: DataProvider,
                 view: MietverhaeltnisView):
        self._dataProvider = dataprovider
        self._view: MietverhaeltnisView = view
        self._whg_id: int = -1

    def startWork(self) -> None:
        self._view.registerSaveCallback(self._onSave)

    def _onSave(self, data: XMietverhaeltnis) -> None:
        msg = self._validate(data)
        if msg:
            messagebox.showerror('Falsche Eingabe', msg)
            return

        try:
            #self._dataProvider.updateWohnungDetails(data)
            pass
        except WvException as ex:
            messagebox.showerror("Speichern fehlgeschlagen", ex.message())

    def _validate(self, data: XWohnungDetails) -> str or None:
        return None

    def _loadData(self) -> None:
        try:
            # details: XWohnungDetails = \
            #     self._dataProvider.getWohnungDetails(self._whg_id)
            # self._view.setData(details)
            pass
        except WvException as ex:
            messagebox.showerror("Uuuups!", ex.message())

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadData()

    def clear(self):
        # called by wvcontroller: clear view and all member variables
        pass


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
