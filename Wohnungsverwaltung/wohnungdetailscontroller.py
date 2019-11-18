#import libs
from libs import *
from wohnungdetailsview import WohnungDetailsView
from business import DataProvider, WvException
from interfaces import XWohnungDetails

class WohnungDetailsController:
    def __init__(self, dataprovider: DataProvider,
                 view: WohnungDetailsView):
        self._dataProvider = dataprovider
        self._view: WohnungDetailsView = view
        self._whg_id: int = -1

    def startWork(self) -> None:
        self._view.registerSaveCallback(self._onSave)

    def _onSave(self, data: XWohnungDetails) -> None:
        msg = self._validate(data)
        if msg:
            messagebox.showerror('Falsche Eingabe', msg)
            return

        try:
            self._dataProvider.updateWohnungDetails(data)
        except WvException as ex:
            messagebox.showerror("Speichern fehlgeschlagen", ex.message())

    def _validate(self, data: XWohnungDetails) -> str or None:
        return None

    def _loadData(self) -> None:
        try:
            details: XWohnungDetails = \
                self._dataProvider.getWohnungDetails(self._whg_id)
            self._view.setData(details)
        except WvException as ex:
            messagebox.showerror("Uuuups!", ex.message())

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadData()


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

    ctrl = WohnungDetailsController(dp, wv)
    ctrl.startWork()
    ctrl.wohnungSelected(10)

    root.mainloop()

if __name__ == '__main__':
    test()
