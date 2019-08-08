#from tkinter import *
#from tkinter import ttk
from editabletable import GenericEditableTable
from business import DataProvider, DataError, ServiceException
from columndefsprovider import ColumnDefsProvider
from actions import Action

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

    def _onEditRowAction(self, action: int, values: dict) -> str:
        if action == Action.DELETE:
            if 'mea_id' in values and values['mea_id'] > 0:
                try:
                    self._dataProvider.deleteMtlEinAus(values['mea_id'])
                except:
                    return 'Fehler beim Löschen des Datensatzes.'
            else:
                return 'Datensatz muss erst gespeichert werden,\n' \
                       'bevor er gelöscht werden kann!'
        elif action == Action.OK: #update or insert
            #provide whg_id
            valuescopy = dict(values)
            valuescopy['whg_id'] = self._whg_id
            if 'mea_id' in values and values['mea_id'] > 0:
                #update an existing mtlEinAus; first validate
                if not self._validate(values):
                    self._dataProvider.updateMtlEinAus(valuescopy)
            else:
                #insert a new mtlEinAus; first validate
                msg = self._validate(values)
                if not msg:
                    try:
                        retVal = self._dataProvider.insertMtlEinAus(valuescopy)
                        values['mea_id'] = retVal.object_id()
                        li = list()
                        li.append(values)
                        self._tv.appendRows(li)
                    except DataError as e:
                        return e.toString()
                else: #validate provides complaint
                    return msg

        return ''

    def _validate(self, meadaten: dict) -> str or None:
        if not meadaten['miete_netto']:
            return 'Nettomiete muss angegeben sein.'
        if not meadaten['nk_abschlag']:
            return 'Nebenkosten-Abschlag muss angegeben sein.'
        if not meadaten['hg_netto_abschlag']:
            return 'Hausgeld-Netto-Abschlag muss angegeben sein.'
        if not meadaten['ruecklage_zufuehrung']:
            return 'Zuführung zu den Rücklagen muss angegeben sein.'
        if not meadaten['gueltig_ab']:
            return 'Gültig-Ab-Datum muss angegeben sein.'
        return ''

    def wohnungSelected(self, whg_id: int) -> None:
        mea_list = self._dataProvider.getMtlEinAusUebersicht(whg_id)
        self._whg_id = whg_id
        """
        mea_list:
            a list of dictionaries.
            Each dictionary looks like so:
            {
              'mea_id': '11',
              'rg_datum': '2019-02-02',
              'rg_nr': '11',
              'betrag': '44.00',
              'verteilung_jahre': '1',
              'firma': 'superfirma',
              'bemerkung': 'gggg',
              'rg_bezahlt_am': '2019-02-02'
            }
        """
        self._tv.setRows(mea_list)