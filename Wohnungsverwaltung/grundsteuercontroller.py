from editabletable import GenericEditableTable
from business import DataProvider, DataError, ServiceException
from columndefsprovider import ColumnDefsProvider
from actions import Action
import datehelper
#++++++++++++++++++++++++++++++++++++++++++++++++

class GrundsteuerController:
    def __init__(self, dataProvider: DataProvider,
                 gsTableView: GenericEditableTable):
        self._dataProvider = dataProvider
        self._tv = gsTableView
        self._whg_id = None

    def startWork(self) -> None:
        columnDefs = ColumnDefsProvider.getGrundsteuerDefs()
        self._tv.configureTable(columnDefs)
        self._tv.registerActionCallback(self._onEditRowAction)

    def _onEditRowAction(self, action: int, rowItemId: str,
                         values: dict, origvalues: dict):
        tv = self._tv
        if action == Action.CANCEL:
            tv.cancelEditing()
            return

        if action == Action.DELETE:
            if 'gs_id' in values and values['gs_id'] > 0:
                yes: bool = tv.askyesno('Sicherheitsabfrage',
                                              'Diesen Satz wirklich löschen?')
                if yes:
                    try:
                        self._dataProvider.deleteGrundsteuer(values['gs_id'])
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
                # work around a bug in MyText: remove trailing '\n'
                if values['bemerkung'].endswith('\n'):
                    values['bemerkung'] = values['bemerkung'][:-1]

                values['whg_id'] = self._whg_id
                #update or insert?
                if ('gs_id' in values and values['gs_id'] > 0):
                    #update an existing sea record
                    try:
                        self._dataProvider.updateGrundsteuer(values)
                        self._loadGrundsteuerDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())
                else:
                    #insert a new sea record;
                    try:
                        retVal = self._dataProvider.insertGrundsteuer(values)
                        self._loadGrundsteuerDaten()
                    except DataError as e:
                        tv.showError('DB-Fehler', e.toString())

    def _validate(self, gsdaten: dict) -> str or None:
        tv = self._tv
        if not gsdaten['vj_ab']:
            return 'Veranlagungszeitraum fehlt.'
        currentyear = datehelper.getCurrentYear()
        try:
            year = int(gsdaten['vj_ab'])
        except:
            return ''.join(('Ungültiger Eintrag: ', gsdaten['vj_ab'],
                            '\n\nGib eine vierstellige Jahreszahl > ',
                            str(currentyear - 3), ' ein.'))

        if int(gsdaten['vj_ab']) < (currentyear - 1):
            if not tv.askyesno('Veranlagungszeitraum',
                              'Der Veranlagungszeitraum liegt mehr als '
                              'ein Jahr zurück. \nTrotzdem speichern?', True):
                return 'Grundsteuersatz wird nicht gespeichert.'

        if not gsdaten['betrag']:
            return 'Betrag fehlt.'

        return ''

    def wohnungSelected(self, whg_id: int) -> None:
        self._whg_id = whg_id
        self._loadGrundsteuerDaten()

    def _loadGrundsteuerDaten(self) -> None:
        """
        gs_list:
            a list of dictionaries.
            Each dictionary looks like so:
            {
                'gs_id': '1',
                'vj_ab': '2018',
                'betrag': '300',
                'bemerkung': 'ohne Grund'
            }
        """
        gs_list = self._dataProvider.getGrundsteuerData(self._whg_id)
        self._tv.setRows(gs_list)

    def clear(self) -> None:
        self._tv.clear()

def test():
    from tkinter import  Tk
    from tkinter import ttk
    import sys
    sys.path.append('/home/martin/Projects/python/mywidgets')
    try:
        from editabletable import GenericEditableTable, Mappings
    except ImportError:
        print("couldn't import editabletable.")

    dp = DataProvider()
    dp.connect('martin', 'fuenf55')
    root = root = Tk()

    tv = GenericEditableTable(root)
    tv.grid(column=0, row=0, sticky='nswe')
    ctrl = GrundsteuerController(dp, tv)
    ctrl.startWork()
    ctrl.wohnungSelected(1)

    values = {
        'vj_ab': '2018',
        'betrag': '300',
        'bemerkung': 'ohne Grund',
        'whg_id': 1
    }
    #ctrl._onEditRowAction(Action.OK, '', values, None)

    root.mainloop()

if __name__ == '__main__':
    #messagebox.askokcancel("Title", "Message", icon='warning')
    test()