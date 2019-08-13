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
        artcbo = self._tv.getWidget('art')
        artcbo.clear()
        itemlist = [x['art'] for x in self._sea_arten]
        #itemlist.insert(0, '')
        artcbo.setItems(itemlist)
        #artcbo.setIndex(0)

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
                        self._dataProvider.deleteSonstEinAus(values['sea_id'])
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
                # values dictionary: complement 'art_id' using 'art'
                for k in self._sea_arten:
                    if k['art'] == values['art']:
                        values['art_id'] = k['art_id']
                        break

                #complement whg_id
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
                'sea_id': '2',
                'vj': '2020',
                'betrag': '112.00',
                'art': 'Ablöse',
                'bemerkung': 'dfdf\n'
            }
        """
        sea_list = self._dataProvider.getSonstigeEinAusData(self._whg_id)
        self._tv.setRows(sea_list)

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
    ctrl = SonstEinAusController(dp, tv)
    ctrl.startWork()
    ctrl.wohnungSelected(1)

    values = {
        'vj': '2019',
        'betrag': '500',
        'art': 'Sonderumlage',
        'bemerkung': 'ohne Grund',
        'whg_id': 2
    }
    #ctrl._onEditRowAction(Action.OK, '', values, None)

    root.mainloop()

if __name__ == '__main__':
    #messagebox.askokcancel("Title", "Message", icon='warning')
    test()