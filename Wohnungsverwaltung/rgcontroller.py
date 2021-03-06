#from tkinter import *
#from tkinter import ttk
from editabletable import GenericEditableTable
from business import DataProvider, DataError, ServiceException
from columndefsprovider import ColumnDefsProvider
from actions import Action

#++++++++++++++++++++++++++++++++++++++++++++++++

class RechnungController:
    """
    todo:
    Unterscheiden, ob es sich um Erhaltungsaufwand oder Herstellungsaufwand handelt.
    Erhaltungsaufwand kann *nach Belieben des Vermieters* im Jahr der Bezahlung
    oder aber auf bis zu 5 Jahre verteilt abgeschrieben werden.
    Als Erhaltungsaufwand gelten laut Bundesfinanzministerium
    "Aufwendungen für die Erneuerung von bereits vorhandenen Teilen,
    Einrichtungen oder Anlagen". Wichtig ist in diesem Zusammenhang,
    dass die modernisierten oder neuen Gebäudeteile die Funktion der alten Teile
    in vergleichbarer Weise ersetzen.
    Die Verwendungs- oder Nutzungsmöglichkeit soll erhalten oder wiederhergestellt werden.

    Dazu muss
        - ein neues DB-Feld "Erhaltung/Herstellung" eingeführt werden
        - der Rechnung-Tab erweitert werden:
            - sowohl in Tabelle wie auch in Edit-Zeile "Herstellung" bzw. "Erhaltung"
              ergänzt werden
            - im Falle von Erhaltung die Verteilung-Combobox auf 5 Jahre eingeschränkt werden
        - dieser Controller erweitert werden
        - die Klasse AnlageVData erweitert werden
    """
    def __init__(self, dataProvider: DataProvider,
                 rechnungTableView: GenericEditableTable):
        self._dataProvider = dataProvider
        self._tv = rechnungTableView
        self._whg_id = None

    def startWork(self) -> None:
        columnDefs = ColumnDefsProvider.getRechnungDefs()
        self._tv.configureTable(columnDefs)
        self._tv.registerActionCallback(self._onEditRowAction)

    def _onEditRowAction(self, action: int, rowItemId: str,
                         values: dict, origvalues: dict):
        tv = self._tv
        if action == Action.DELETE:
            if 'rg_id' in values and values['rg_id'] > 0:
                yes: bool = tv.askyesno('Sicherheitsabfrage',
                                        'Diesen Satz wirklich löschen?')
                if yes:
                    try:
                        self._dataProvider.deleteRechnung(values['rg_id'])
                        tv.deleteRow(rowItemId)
                    except:
                        tv.showError('DB-Fehler',
                                     'Fehler beim Löschen der Rechnung.')
            else:
                self._tv.showError('Bedienungsfehler',
                                   'Rechnung muss erst gespeichert werden,\n' \
                                   'bevor sie gelöscht werden kann!')
        elif action == Action.OK: #update or insert
            msg = self._validate(values)
            if msg:  # validate provides complaint
                tv.showError('Validierungsfehler', msg)
            else: #validation ok
                #provide whg_id

                # work around a bug in MyText: remove trailing '\n'
                if values['bemerkung'].endswith('\n'):
                    values['bemerkung'] = values['bemerkung'][:-1]

                valuescopy = dict(values)
                valuescopy['whg_id'] = self._whg_id
                if 'rg_id' in values and values['rg_id'] > 0:
                    #update an existing rechnung; first validate
                    try:
                        self._dataProvider.updateRechnung(valuescopy)
                        self._loadRechnungDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())
                else:
                    #insert a new rechnung; first validate
                    try:
                        retVal = self._dataProvider.insertRechnung(valuescopy)
                        self._loadRechnungDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())

    def _validate(self, rgdaten: dict) -> str or None:
        if not rgdaten['rg_datum']:
            return 'Rechnungsdatum muss angegeben sein.'
        if not rgdaten['rg_nr']:
            return 'Rechnungsnummer muss angegeben sein.'
        if not rgdaten['betrag']:
            return 'Rechnungsbetrag muss angegeben sein.'
        if not rgdaten['firma']:
            return 'Firma muss angegeben sein.'
        return ''

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadRechnungDaten()

    def _loadRechnungDaten(self):
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
        rg_list = self._dataProvider.getRechnungsUebersicht(self._whg_id)
        self._tv.setRows(rg_list)

    def clear(self) -> None:
        self._tv.clear()