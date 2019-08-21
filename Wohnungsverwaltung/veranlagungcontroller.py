
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
        self._view.clearAfa()
        self._vj = None
        try:
            newVj = int(newVj)
            self._loadAfaData(newVj)
            self._vj = newVj
        except:
            pass

    def _onSave(self, veranlagData: dict):
        print('VeranlagungsController._onSave')
        self._handleSave(veranlagData)
        self._view.setSaveButtonEnabled(False)

        msg = self._validate(veranlagData)
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

    def _handleSave(self, data: dict):
        """
        :param data:
        <class 'dict'>:
        {
            'angeschafft_am': xx.xx.xxxx,
            'einhwert_az': 343434343434
            'vj_ab': '2018',
            'art_afa': 'linear',
            'prozent': '2.23',
            'afa_wie_vorjahr': 'Ja',
            'betrag': '234.0'
        }

        :return:
        """
        self._handleSaveAfa(data)

        self._loadVeranlagungData(self._vj)

    def _handleSaveAfa(self, data: dict):
        data['lin_deg_knz'] = 'l' if data['art_afa'] == 'linear' else 'd'
        data['afa_wie_vorjahr'] = 'J' if data['afa_wie_vorjahr'] == 'Ja' else 'N'
        #check if update or insert
        id: int = self._dataProvider.getAfaId(self._whg_id, int(data['vj_ab']))
        if id > 0:
            #update existing AfA record
            data['afa_id'] = id
            del data['vj_ab']  #vj_ab is part of the functional key - never update!
            self._dataProvider.updateAfaData(data)
        else:
            #insert new AfA record
            data['whg_id'] = self._whg_id
            self._dataProvider.insertAfaData(data)

    def _handleSaveWhg(self, data: dict):
        """
        :param data:
        {
            'angeschafft_am': xx.xx.xxxx or None
            'einhwert_az':xxxxxxxxxxxxxxx
        }
        :return:
        """
        angeschafft_am = data['angeschafft_am']
        if angeschafft_am:
            angeschafft_am = datehelper.convertEurToIso(angeschafft_am)


    def wohnungSelected(self, whg_id: int) -> None:
        print('veranlagungscontroller: wohnungselected: ', whg_id)
        self._whg_id = whg_id
        #get identifying data for selected flat:
        d = self._dataProvider.getWohnungIdentifikation(whg_id)
        """
        {
            'plz': '90429', 
            'ort': 'Nürnberg', 
            'strasse': 'Mendelstr. 24', 
            'whg_bez': '3. OG rechts', 
            'einhwert_az': None, 
            'angeschafft_am': None
        }
        """
        #set the views top label
        whgident = ''.join((d['ort'], ', ', d['strasse'], ', ', d['whg_bez']))
        self._view.setWohnungIdent(whgident)

        #set wohnung data related to Veranlagung
        angeschafftAm = None
        if d['angeschafft_am']:
            angeschafftAm = datehelper.convertIsoToEur(d['angeschafft_am'])
        self._view.setWohungData(angeschafftAm, d['einhwert_az'])
        self._view.clearAfa()

        #and if a Vj is set get selected flat's AfA data as well:
        if self._vj:
            self._loadAfaData(self._vj)

    def _loadVeranlagungData(self, vj: int):
        """
        called after having saved modified data
        :param vj:
        :return:
        """
        data = self._dataProvider.getVeranlagungsdata(self._whg_id, vj)

    def _loadAfaData(self, vj: int):
        """
        called when Vj was changed by user
        :param vj: changed Vj
        :return: None
        """
        data = self._dataProvider.getAfaData(self._whg_id, vj)
        """
        data = {
            'afa_id': '2',
            'betrag': '2345',
            'prozent': '2.23',
            'lin_deg_knz': 'l',
            'afa_wie_vorjahr': 'Ja'
        }
        """
        if data:
            data['art_afa'] = 'linear' if data['lin_deg_knz'] == 'l' else 'degressiv'
            self._view.setAfaData(data)
            #self._view.setSaveButtonEnabled(False)

            enabled = True if not self._validate(data) else False
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