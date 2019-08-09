#from tkinter import *
#from tkinter import ttk
from editabletable import GenericEditableTable
from business import DataProvider, DataError, ServiceException
from columndefsprovider import ColumnDefsProvider
from actions import Action
import datehelper
#++++++++++++++++++++++++++++++++++++++++++++++++

class MtlEinAusController:
    def __init__(self, dataProvider: DataProvider,
                 mtleaTableView: GenericEditableTable):
        self._dataProvider = dataProvider
        self._tv = mtleaTableView
        self._whg_id = None

    def startWork(self) -> None:
        columnDefs = ColumnDefsProvider.getMonatlicheEinAusDefs()
        self._tv.configureTable(columnDefs)
        self._tv.registerActionCallback(self._onEditRowAction)

    def _onEditRowAction(self, action: int, rowItemId: str, values: dict):
        tv = self._tv
        if action == Action.DELETE:
            if 'mea_id' in values and values['mea_id'] > 0:
                yes: bool = tv.askyesno('Sicherheitsabfrage',
                                              'Diesen Satz wirklich löschen?')
                if yes:
                    try:
                        self._dataProvider.deleteMtlEinAus(values['mea_id'])
                        tv.deleteRow(rowItemId)
                    except:
                        tv.showError('DB-Fehler',
                                     'Fehler beim Löschen des Datensatzes.')
            else:
                self._tv.showError('Bedienungsfehler',
                                   'Datensatz muss erst gespeichert werden,\n' \
                                   'bevor er gelöscht werden kann!')
        elif action == Action.OK: #update or insert
            msg = self._validate(values)
            if msg: #validate provides complaint
                tv.showError('Validierungsfehler', msg)
            else: #validation ok
                #provide whg_id
                valuescopy = dict(values)
                valuescopy['whg_id'] = self._whg_id
                if 'mea_id' in values and values['mea_id'] > 0:
                    #update an existing mtlEinAus;
                    try:
                        self._dataProvider.updateMtlEinAus(valuescopy)
                        self._loadMeaDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())
                else:
                    #insert a new mtlEinAus;
                    try:
                        retVal = self._dataProvider.insertMtlEinAus(valuescopy)
                        self._loadMeaDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())

    def _validate(self, meadaten: dict) -> str or None:
        if not meadaten['netto_miete']:
            return 'Nettomiete muss angegeben sein.'
        if not meadaten['nk_abschlag']:
            return 'Nebenkosten-Abschlag muss angegeben sein.'
        if not meadaten['hg_netto_abschlag']:
            return 'Hausgeld-Netto-Abschlag muss angegeben sein.'
        if not meadaten['ruecklage_zufuehr']:
            return 'Zuführung zu den Rücklagen muss angegeben sein.'
        if not meadaten['gueltig_ab']:
            return 'Gültig-Ab-Datum muss angegeben sein.'
        if meadaten['gueltig_ab'] and meadaten['gueltig_bis']:
            rc = datehelper.compareEurDates(meadaten['gueltig_ab'],
                                            meadaten['gueltig_bis'])
            if rc > 0:
                return 'Wenn ein Gültig-Bis-Datum angegeben ist, ' \
                       'muss es größer sein als das Gültig-Ab-Datum.'
        return ''

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadMeaDaten()

    def _loadMeaDaten(self) -> None:
        """
        mea_list:
            a list of dictionaries.
            Each dictionary looks like so:
            {
              'mea_id': '1',
              'gueltig_ab': '20.12.2019',
              'gueltig_bis': '',
              'netto_miete': '300.00',
              'nk_abschlag': '22.00',
              'brutto_miete': '322.00',
              'hg_netto_abschlag': '44.00',
              'ruecklage_zufuehr': '33.00',
              'hg_brutto': '77.00',
              'ueberschuss': '245.00',
              'bemerkung': 'eadaqwe'
            }
        """
        mea_list = self._dataProvider.getMtlEinAusData(self._whg_id)
        self._tv.setRows(mea_list)

