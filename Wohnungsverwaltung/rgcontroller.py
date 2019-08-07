#from tkinter import *
#from tkinter import ttk
from editabletable import GenericEditableTable
from business import DataProvider, DataError, ServiceException
from columndefsprovider import ColumnDefsProvider
from actions import Action

#++++++++++++++++++++++++++++++++++++++++++++++++

class RechnungController:
    def __init__(self, dataProvider: DataProvider,
                 rechnungTableView: GenericEditableTable):
        self._dataProvider = dataProvider
        self._tv = rechnungTableView
        self._whg_id = None

    def startWork(self) -> None:
        columnDefs = ColumnDefsProvider.getRechnungDefs()
        self._tv.configureTable(columnDefs)
        self._tv.registerActionCallback(self._onEditRowAction)

    def _onEditRowAction(self, action: int, values: dict) -> str:
        if action == Action.DELETE:
            if 'rg_id' in values and values['rg_id'] > 0:
                try:
                    self._dataProvider.deleteRechnung(values['rg_id'])
                except:
                    return 'Fehler beim Löschen der Rechnung.'
            else:
                return 'Rechnungssatz muss erst gespeichert werden,\n' \
                       'bevor er gelöscht werden kann!'
        elif action == Action.OK:
            #provide whg_id
            valuescopy = dict(values)
            valuescopy['whg_id'] = self._whg_id
            if 'rg_id' in values and values['rg_id'] > 0:
                #update an existing rechnung; first validate
                if self._validate(values):
                    self._dataProvider.updateRechnung(valuescopy)
            else:
                #insert a new rechnung; first validate
                msg = self._validate(values)
                if not msg:
                    try:
                        retVal = self._dataProvider.insertRechnung(valuescopy)
                        values['rg_id'] = retVal.object_id()
                        li = list()
                        li.append(values)
                        self._tv.appendRows(li)
                    except DataError as e:
                        return e.toString()
                else: #validate provides complaint
                    return msg

        return ''

    def _validate(self, rgdaten: dict) -> str or None:
        return ''

    def wohnungSelected(self, whg_id: int) -> None:
        rg_list = self._dataProvider.getRechnungsUebersicht(whg_id)
        self._whg_id = whg_id
        """
        rg_list:
            a list of dictionaries.
            Each dictionary looks like so:
            {
              'rg_id': '11',
              'rg_datum': '2019-02-02',
              'rg_nr': '11',
              'betrag': '44.00',
              'verteilung_jahre': '1',
              'firma': 'superfirma',
              'bemerkung': 'gggg',
              'rg_bezahlt_am': '2019-02-02'
            }
        """
        self._tv.setRows(rg_list)
        self._tv.alignColumn('Betrag', 'e')
        self._tv.alignColumn('Jhre AfA', 'e')
        self._tv.makeColumnWidthFit('Jhre AfA')