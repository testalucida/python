
from business import DataProvider, DataError, ServiceException
from mywidgets import TextEntry
from actions import Action
from veranlagungview import VeranlagungView
import datehelper

class VeranlagungController:
    def __init__(self, dataProvider: DataProvider,
                 veranlagungView: VeranlagungView):
        self._dataProvider = dataProvider
        self._view = veranlagungView
        self._whg_id = None
        self._afadata = None

    def startWork(self) -> None:
        #todo: register Save-Callback
        pass

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadVeranlagungData()

    def _loadVeranlagungData(self):
        pass

def test():
    from tkinter import  Tk
    from tkinter import ttk

    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    root = root = Tk()

    style = ttk.Style()
    style.theme_use('clam')

    tv = VeranlagungView(root)
    tv.grid(column=0, row=0, sticky='nswe', padx=10, pady=10)
    ctrl = VeranlagungController(dp, tv)
    ctrl.startWork()
    ctrl.wohnungSelected(1)

    root.mainloop()

if __name__ == '__main__':
    test()