
from business import DataProvider, DataError, ServiceException
from tkinter import messagebox
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
        self._view.registerSaveCallback(self._onSave)
        self._view.registerCreateAnlageVCallback(self._onCreateAnlageV)
        self._view.setSaveButtonEnabled(False)
        self._view.setCreateAnlageVButtonEnabled(False)

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

    def _onSave(self, afa: dict):
        print('VeranlagungsController._onSave')
        self._handleSaveAfa(afa)
        self._view.setSaveButtonEnabled(False)

        msg = self._validate(afa)
        if msg:
            messagebox.showerror('Validierungsfehler', msg)
        else:
            self._view.setCreateAnlageVButtonEnabled(True)

    def _onCreateAnlageV(self, afa: dict):
        print('VeranlagungsController._onCreateAnlageV')

    def _validate(self, afa: dict) -> str or None:
        if not self._vj:
            return 'Es ist kein Veranlagungsjahr eingestellt.'

        if not afa['art_afa']:
            return 'Die Art der Abschreibung muss angegeben werden ' \
                   '(linear/degressiv).'

        if not afa['afa_wie_vorjahr']:
            return 'Die Angabe fehlt, ' \
                   'ob die AfA-Angaben die gleichen wie im Vorjahr sind.'

        if not afa['betrag']:
            return 'Der AfA-Betrag muss angegeben sein.'

        return None

    def _handleSaveAfa(self, afa: dict):
        """
        :param afa:
        <class 'dict'>:
        {
            'vj_ab': '2018',
            'art_afa': 'linear',
            'prozent': '2.23',
            'afa_wie_vorjahr': 'Ja',
            'betrag': '234.0'
        }

        :return:
        """
        afa['lin_deg_knz'] = 'l' if afa['art_afa'] == 'linear' else 'd'
        afa['afa_wie_vorjahr'] = 'J' if afa['afa_wie_vorjahr'] == 'Ja' else 'N'
        #check if update or insert
        id: int = self._dataProvider.getAfaId(self._whg_id, int(afa['vj_ab']))
        if id > 0:
            #update existing AfA record
            afa['afa_id'] = id
            del afa['vj_ab']  #vj_ab is part of the functional key - never update!
            self._dataProvider.updateAfaData(afa)
        else:
            #insert new AfA record
            afa['whg_id'] = self._whg_id
            self._dataProvider.insertAfaData(afa)
            
        self._loadVeranlagungData(self._vj)


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
            self._view.setSaveButtonEnabled(False)

            enabled: bool = True
            if not self._validate(data):
                enabled = False
            self._view.setCreateAnlageVButtonEnabled(enabled)

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