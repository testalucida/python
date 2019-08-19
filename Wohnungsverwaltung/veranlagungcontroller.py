
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
        self._vj = None

    def startWork(self) -> None:
        self._view.registerVjChangeCallback(self._onVjChanged)

    def _onVjChanged(self, newVj: str):
        print('onVjChanged: ', newVj)
        self._view.clear()
        self._vj = None
        try:
            newVj = int(newVj)
            self._loadVeranlagungData(newVj)
            self._vj = newVj
        except:
            pass

    def wohnungSelected(self, whg_id: int) -> None:
        print('veranlagungscontroller: wohnungselected: ', whg_id)
        self._whg_id = whg_id
        self._view.clear()
        if self._vj:
            self._loadVeranlagungData(self._vj)

    def _loadVeranlagungData(self, vj: int):
        """
        data = {
            'afa_id': '2',
            'betrag': '2345',
            'prozent': '2.23',
            'lin_deg_knz': 'l',
            'afa_wie_vorjahr': 'Ja'
        }
        :return:
        """
        print('loadVeranlagungsdata: ', self._whg_id, ' ', vj)
        data = self._dataProvider.getAfaData(self._whg_id, vj)
        if data:
            data['art_afa'] = 'linear' if data['lin_deg_knz'] == 'l' else 'degressiv'
            self._view.setAfaData(data)

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