
from business import DataProvider, DataError, ServiceException
from mywidgets import TextEntry
from actions import Action
from stammdatenview import StammdatenView
import datehelper

class StammdatenController:
    def __init__(self, dataProvider: DataProvider,
                 stammdatenView: StammdatenView):
        self._dataProvider = dataProvider
        self._view = stammdatenView
        self._whg_id = None
        self._vermieterdata = None
        self._wohnungdata = None
        self._afadata = None

    def startWork(self) -> None:
        #todo: register Save-Callback
        pass

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadStammdaten()

    def _loadStammdaten(self):
        self._vermieterdata: dict = \
            self._dataProvider.getVermieterData(self._whg_id)
        """
        {
            'v_id': '1', 
            'name': 'Kendel', 
            'vorname': 'Martin', 
            'strasse': '', 
            'plz': '', 
            'ort': '', 
            'steuernummer': '217/235/50499'
        }
        """
        self._view.setVermieterData(self._vermieterdata)

        self._wohnungdata: dict = \
            self._dataProvider.getWohnungIdentifikation(self._whg_id)
        self._view.setWohungData(self._wohnungdata)

def test():
    from tkinter import  Tk
    from tkinter import ttk

    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    root = root = Tk()

    style = ttk.Style()
    style.theme_use('clam')

    tv = StammdatenView(root)
    tv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    ctrl = StammdatenController(dp, tv)
    ctrl.startWork()
    ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()