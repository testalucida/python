from editabletable import GenericEditableTable
from business import DataProvider, DataError, ServiceException
from columndefsprovider import ColumnDefsProvider
from actions import Action
import datehelper
#++++++++++++++++++++++++++++++++++++++++++++++++

class SonstEinAusController:
    def __init__(self, dataProvider: DataProvider,
                 seaTableView: GenericEditableTable):
        self._dataProvider = dataProvider
        self._tv = seaTableView
        self._sea_arten = None
        self._whg_id = None

    def startWork(self) -> None:
        columnDefs = ColumnDefsProvider.getSonstigeEinAusDefs()
        self._tv.configureTable(columnDefs)
        self._sea_arten = self._dataProvider.getSonstigeEinAusArten()
        self._tv.registerActionCallback(self._onEditRowAction)

    def _onEditRowAction(self, action: int, rowItemId: str,
                         values: dict, origvalues: dict):
        tv = self._tv
        if action == Action.CANCEL:
            tv.cancelEditing()
            return

        if action == Action.DELETE:
            if 'sea_id' in values and values['sea_id'] > 0:
                yes: bool = tv.askyesno('Sicherheitsabfrage',
                                              'Diesen Satz wirklich löschen?')
                if yes:
                    try:
                        self._dataProvider.deleteMtlEinAus(values['sea_id'])
                        tv.deleteRow(rowItemId)
                    except:
                        tv.showError('DB-Fehler',
                                     'Fehler beim Löschen des Datensatzes.')
            else:
                self._tv.showError('Bedienungsfehler',
                                   'Datensatz muss erst gespeichert werden,\n' \
                                   'bevor er gelöscht werden kann!')
        elif action == Action.OK: #update or insert
            #validation
            msg = self._validate(values)
            if msg: #validate provides complaint
                tv.showError('Validierungsfehler', msg)

            else: #validation ok
                values['whg_id'] = self._whg_id
                #update or insert?
                if ('sea_id' in values and values['sea_id'] > 0):
                    #update an existing sea record
                    try:
                        self._dataProvider.updateSonstEinAus(values)
                        self._loadSeaDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())
                else:
                    #insert a new sea record;
                    try:
                        retVal = self._dataProvider.insertSonstEinAus(values)
                        self._loadSeaDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())

    def _validate(self, meadaten: dict) -> str or None:
        return ''

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadSeaDaten()

    def _loadSeaDaten(self) -> None:
        """
        sea_list:
            a list of dictionaries.
            Each dictionary looks like so:
            {

            }
        """
        sea_list = self._dataProvider.getSonstigeEinAusData(self._whg_id)
        self._tv.setRows(sea_list)

def test():

    ctrl = SonstEinAusController(None, None)

if __name__ == '__main__':
    #messagebox.askokcancel("Title", "Message", icon='warning')
    test()