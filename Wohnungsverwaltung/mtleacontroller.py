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

    def _onEditRowAction(self, action: int, rowItemId: str,
                         values: dict, origvalues: dict):
        tv = self._tv
        if action == Action.CANCEL:
            tv.cancelEditing()
            return

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
            #first simple validation
            msg = self._validate(values)
            if msg: #validate provides complaint
                tv.showError('Validierungsfehler', msg)

            else: #simple validation ok
                #update or insert?
                isUpdate: bool = \
                    True if ('mea_id' in values and values['mea_id'] > 0) \
                        else False
                #extended validation: check periods of payment are not intersecting
                #first get current mtlea records from database
                mea_list = self._dataProvider.getCurrentAndFutureMtlEinAus(self._whg_id)
                #in case of update we remove the relating dictionary from mea_list:
                if isUpdate:
                    for mea in mea_list:
                        if int(mea['mea_id']) == int(values['mea_id']):
                            mea_list.remove(mea)
                            break
                msg: str = ''
                if len(mea_list) > 0:
                    msg = self._periodsOverlapping(values['gueltig_ab'],
                                            values['gueltig_bis'],
                                            mea_list)
                if msg:
                    tv.showError('Inkonsistente Zahlungszeiträume',
                                 ''.join(('Zahlungszeiträume dürfen sich nicht überschneiden:\n',
                                          msg)))
                else:
                    #work around a bug in MyText: remove trailing '\n'
                    if values['bemerkung'].endswith('\n'):
                        values['bemerkung'] = values['bemerkung'][:-1]
                    #provide whg_id
                    values['whg_id'] = self._whg_id
                    if isUpdate:
                        #update an existing mtlEinAus;
                        try:
                            #if we have a change in payment, show a warning as to tax impact
                            if values['gueltig_ab'] == origvalues['gueltig_ab'] and \
                                    datehelper.compareToToday(values['gueltig_ab']) < 0:
                                if values['netto_miete'] != origvalues['netto_miete'] or \
                                    values['nk_abschlag'] != origvalues['nk_abschlag'] or \
                                    values['hg_netto_abschlag'] != origvalues['hg_netto_abschlag'] or \
                                    values['ruecklage_zufuehr'] != origvalues['ruecklage_zufuehr']:
                                    yes = tv.askyesno('Achtung',
                                                ''.join(('Die Änderung der Zahlung wirkt ab dem ',
                                                         values['gueltig_ab'],
                                                         ', \nalso auf einen schon vergangenen Zeitraum.',
                                                         '\nDies kann steuerliche Auswirkungen haben.\n',
                                                         '\nTrotzdem ändern?')), True)
                                    if not yes: return

                            self._dataProvider.updateMtlEinAus(values)
                            self._loadMeaDaten()
                        except DataError as e:
                            tv.showError('DB-Fehler', e.toString())
                    else:
                        #insert a new mtlEinAus;
                        try:
                            retVal = self._dataProvider.insertMtlEinAus(values)
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

    def _periodsOverlapping(self, gueltig_ab: str, gueltig_bis: str, periodlist: list) -> str:
        """
        checks if a given period overlaps with other periods in a datelist.
        All dates in eur formatted strings expected ('21.08.2018')
        :param gueltig_bis:
        :param datelist: a list of dictionaries containing the key 'gueltig_ab' and 'gueltig_bis'
        :return: '' if nothing overlaps otherwise a message containing the faulty period
        """
        gueltig_bis_cpy = '31.12.2999' if gueltig_bis == '' else gueltig_bis
        for period in periodlist:
            period_bis = '31.12.2999' if period['gueltig_bis'] == '' else period['gueltig_bis']
            if datehelper.isWithin(gueltig_ab, period['gueltig_ab'], period_bis) or \
               datehelper.isWithin(gueltig_bis_cpy, period['gueltig_ab'], period_bis) or \
               datehelper.isWithin(period['gueltig_ab'], gueltig_ab, gueltig_bis_cpy) or \
               datehelper.isWithin(period_bis, gueltig_ab, gueltig_bis_cpy):
                gueltig_bis_cpy = '<unbegrenzt>' \
                    if gueltig_bis_cpy == '31.12.2999' else gueltig_bis_cpy
                period_bis = '<unbegrenzt>' \
                    if period_bis == '31.12.2999' else period['gueltig_bis']
                return ''.join(('Der Zeitraum\n', gueltig_ab, ' bis ', gueltig_bis_cpy,
                                '\nüberschneidet sich mit dem Zeitraum\n',
                                period['gueltig_ab'], ' bis ', period_bis))
        return ''

    def _createSortKey(self, period: dict):
        return datehelper.convertEurToIso(period['gueltig_ab'])

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

    def clear(self) -> None:
        self._tv.clear()

def test():
    gueltig_ab = '01.01.2020'
    gueltig_bis = ''
    p1 = {'gueltig_ab': '08.10.2016', 'gueltig_bis': '31.10.2019' }
    p2 = {'gueltig_ab': '01.11.2019', 'gueltig_bis': '31.12.2020'}
    l = list()
    l.append(p1)
    l.append(p2)
    ctrl = MtlEinAusController(None, None)
    msg = ctrl._periodsOverlapping(gueltig_ab, gueltig_bis, l)
    print('overlapping: ', msg)

if __name__ == '__main__':
    #messagebox.askokcancel("Title", "Message", icon='warning')
    test()