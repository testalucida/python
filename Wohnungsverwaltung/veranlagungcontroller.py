
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
        #print('onVjChanged: ', newVj)
        #todo: check if there are any unsaved changes
        self._view.clearAfa()
        self._vj = None
        try:
            newVj = int(newVj)
            self._loadAfaData(newVj)
            self._vj = newVj
        except:
            pass

    # def _onSaveXXX(self, veranlagData: dict):
    #     print('VeranlagungsController._onSave')
    #     self._handleSave(veranlagData)
    #     self._view.setSaveButtonEnabled(False)
    #
    #     msg = self._validate(veranlagData)
    #     if msg:
    #         messagebox.showerror('Validierungsfehler', msg)
    #     else:
    #         self._view.setCreateAnlageVButtonEnabled(True)

    def _onCreateAnlageV(self, afa: dict):
        print('VeranlagungsController._onCreateAnlageV')

    def _validateWhg(self, whg: dict) -> str or None:
        """
        :param whg:
        {
            'angeschafft_am': xx.xx.xxxx,
            'einhwert_az': 343434343434,
            'steuerl_zurechng_mann': 100,
            'steuerl_zurechng_frau': 0
        }
        :return: str or None
        """
        if not whg['angeschafft_am']:
            return 'Ins Feld "Angeschafft am" muss ein gültiges Datum eingetragen werden.'

        if not datehelper.isValidEurDatestring(whg['angeschafft_am']):
            return 'Das eingegebene "Angeschafft am"-Datum entspricht nicht ' \
                   'der Form "tt.mm.jjjj".'

        if not whg['einhwert_az']:
            return 'Einheitswert-Aktenzeichen fehlt.'

        if not whg['steuerl_zurechng_mann']:
            return 'Es fehlt die Angabe, zu wieviel Prozent das steuerliche ' \
                   'Ergebnis dem Ehemann angerechnet werden soll'

        if not whg['steuerl_zurechng_frau']:
            return 'Es fehlt die Angabe, zu wieviel Prozent das steuerliche ' \
                   'Ergebnis der Ehefrau angerechnet werden soll'

        zurechng_mann = int(whg['steuerl_zurechng_mann'])
        zurechng_frau = int(whg['steuerl_zurechng_frau'])

        if zurechng_mann > 100 or zurechng_frau > 100:
            return 'Der Zuordnungswert darf "100" nicht übersteigen'

        if zurechng_mann + zurechng_frau != 100:
            return 'Die Summe der Zurechnungswerte muss 100 betragen'

        return None

    def _validateAfa(self, afa: dict) -> str or None:
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

    def _onSave__(self, data: dict):
        """
        check what kind of data to save: wohnung and/or Afa
        if afa: handleSaveAfa
        if wohnung: handleSaveWhg
        after having saved re-load appropriate parts of data (_loadAfaData /
        _loadWhgData)
        resp. _loadAllData if both parts were saved.
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

        :return: None
        """
        rcWhg = self._handleWhgData(data)
        if not rcWhg['isWhgValid']: return

        rcAfa = self._handleAfaData(data)
        if not rcAfa['isAfaValid']: return

        #which data to load after having saved:
        if rcWhg['isWhgModified'] and rcAfa['isAfaModified']:
            self._loadAllData(self._vj)
        elif rcAfa['isAfaModified']:
            self._loadAfaData(self._vj)
        elif rcWhg['isWhgModified']:
            self._loadWhgData()

        if rcWhg['isWhgValid'] and rcAfa['isAfaValid']:
            self._view.setCreateAnlageVButtonEnabled(True)

    def _onSave(self, data: dict) -> None:
        #save anything even if it's not valid or not complete.
        #validation will be performed when the user hits 'createAnlageV'
        isWhgModified = self._view.isWhgModified()
        whgMsg = afaMsg = None
        if isWhgModified:
            self._handleSaveWhg(data)
            whgMsg = self._validateWhg(data)
            if whgMsg:
                messagebox.showwarning(
                    'Wohnungsdaten wurden gespeichert, aber...', whgMsg)

        rcAfa = self._handleAfaData(data)

        if isWhgModified and rcAfa['isAfaModified'] and rcAfa['isAfaValid']:
            self._loadAllData(self._vj)
        else:
            if rcAfa['isAfaModified'] and rcAfa['isAfaValid']:
                self._loadAfaData(self._vj)
            if isWhgModified:
                self._loadWhgData()

        self._view.setCreateAnlageVButtonEnabled(
            (whgMsg is None and rcAfa['isAfaValid']))

    def _handleWhgData(self, data: dict) -> dict:
        msg = self._validateWhg(data)
        rc = {
            'isWhgModified': self._view.isWhgModified(),
            'isWhgValid': True if not msg else False
        }

        if rc['isWhgModified']:
            if rc['isWhgValid']:
                self._handleSaveWhg(data)
            else:
                messagebox.showerror('Validierungsfehler', msg)
                #self._view.setSaveButtonEnabled(True)
        return rc

    def _handleAfaData(self, data:dict) -> dict:
        msg = self._validateAfa(data)
        rc = {
            'isAfaModified': self._view.isAfaModified(),
            'isAfaValid': True if not msg else False
        }

        if rc['isAfaModified']:
            if rc['isAfaValid']:
                self._handleSaveAfa(data)
            else:
                messagebox.showerror('Validierungsfehler', msg)
                #self._view.setSaveButtonEnabled(True)
        return rc

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
            'einhwert_az':xxxxxxxxxxxxxxx,
            'steuerl_zurechng_mann': nn,
            'steuerl_zurechng_frau': nn
        }
        :return:
        """
        datacopy = dict(data)
        datacopy['angeschafft_am'] = datehelper.convertEurToIso(datacopy['angeschafft_am'])
        datacopy['whg_id'] = self._whg_id
        self._dataProvider.updateWhgVeranlagData(datacopy)

    def wohnungSelected(self, whg_id: int) -> None:
        #print('veranlagungscontroller: wohnungselected: ', whg_id)
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
            'angeschafft_am': None,
            'steuerl_zurechng_mann: 100,
            'steuerl_zurechng_frau: 0
        }
        """
        #set the views top label
        whgident = ''.join((d['ort'], ', ', d['strasse'], ', ', d['whg_bez']))
        self._view.setWohnungIdent(whgident)

        #set wohnung data related to Veranlagung
        self._view.setWohnungData(d['angeschafft_am'], d['einhwert_az'],
                                 int(d['steuerl_zurechng_mann']),
                                 int(d['steuerl_zurechng_frau']))
        self._view.clearAfa()

        #and if a Vj is set get selected flat's AfA data as well:
        if self._vj:
            self._loadAfaData(self._vj)

    def _loadAllData(self, vj: int):
        """
        called after having saved modified data
        :param vj:
        :return:
        """
        data = self._dataProvider.getVeranlagungData(self._whg_id, vj)
        if data:
            self._view.setWohnungData(data['angeschafft_am'], data['einhwert_az'],
                                     data['steuerl_zurechng_mann'],
                                     data['steuerl_zurechng_frau'])
            self._view.setAfaAndVwData(data)

    def _loadWhgData(self):
        """
        called when wohnung data (angeschafft_am and einhwert_az) was changed
        by user
        :param vj: Vj
        :return: None
        """
        data = self._dataProvider.getWohnungIdentifikation(self._whg_id)
        self._view.setWohnungData(data['angeschafft_am'], data['einhwert_az'],
                                 data['steuerl_zurechng_mann'],
                                 data['steuerl_zurechng_frau'])

    def _loadAfaData(self, vj: int):
        """
        called when Vj was changed by user
        :param vj: changed Vj
        :return: None
        """
        data = self._dataProvider.getAfa(self._whg_id, vj)
        """
        data = {
            'afa_id': '2',
            'betrag': '2345',
            'prozent': '2.23',
            'lin_deg_knz': 'l',
            'afa_wie_vorjahr': 'Ja',
            'verwaltkosten': 200,
            'art_afa': 'linear'
        }
        """
        self._view.setAfaAndVwData(data) #must be done even if data is none
        enabled = False
        if data:
            enabled = True if not self._validateAfa(data) else False
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