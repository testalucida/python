import json
import datetime
from typing import Dict, List, Text
from business import DataProvider
import datehelper
from interfaces import XErhaltungsaufwand

class AnlageVData:
    """
    Sammelt alle Daten, die zur Erstellung der Anlage V für eine Wohnung
    für ein Veranlagungsjahr benötigt werden
    und schreibt sie in eine JSON-Schnittstelle mit folgendem Aufbau:
{
   "_comment":"Alle Daten, die für die Anlage V benötigt werden",
   "vj": 2018,
   "zeilen":[
      {
         "nr":1,
         "felder":[
            {
               "name":"Name",
               "value":"Richter"
            }
         ]
      },
      {
         "nr":2,
         "felder":[
            {
               "name":"Vorname",
               "value":"Paul"
            }
         ]
      },
      {
         "nr":3,
         "felder":[
            {
               "name":"Steuernummer",
               "value":"135/555/12345"
            },
            {
               "name":"lfd. Nr. der Anlage",
               "value":2
            }
         ]
      }
   ]
}
    """
    def __init__(self, whg_id: int, anlage_nr: int, vj: int, dataprovider: DataProvider):
        self._whg_id = whg_id
        self._anlage_nr = anlage_nr
        self._vj = vj
        self._xdatadict = dict() #Dictionary für die Schnittstellendaten
        #self._zeilenlist = list() #liste der Zeilen,
                                  # die dem Schnittstellendict. hinzugefügt wird
        self._dataProvider = dataprovider
        self._savePath = '/home/martin/Projects/python/Wohnungsverwaltung'
        self._log = None
        self._wohnungIdent = None
        self._stammdaten = None
        self._summe_einnahmen = 0
        self._summe_wk = 0

    def _checkForSavePath(self) -> None:
        """
        Setzt einen vom Default abweichenden Pfad.
        :param path: der gewünschte Pfad
        :return: None
        """
        jsonfile = "/home/martin/Projects/python/Wohnungsverwaltung/anlagevconfig.json"
        try:
            f = open(jsonfile)
            j = json.load(f)
        except:
            pass # no file specified

    def startWork(self) -> None:
        """
        - prüft, ob es im current directory eine Config-Datei gibt,
          die einen alternativen SavePath vorgibt
        - sammelt die notwendigen Daten:
            - Mieteinnahmen
            - vereinnahmte Nebenkostenabschläge
            - bezahlte Hausgelder ohne Rücklagen-Zuführung
            - vereinnahmte und verausgabte NK- und Hausgeld-
              Abrechnungen (die das Vj-Vorjahr betreffen)
            - Rechnungen
            - sonstige Einnahmen und Ausgaben, Grundsteuer etc.
            - AfA-Informationen
        - erstellt aus diesen Daten ein Dictionary, das als
          JSON-Struktur in die spezifizierte Datei geschrieben
          wird
        - ruft das C++ - Programm auf, das diese Schnittstelle
          einliest und das Drucken übernimmt.
        :return: None
        """
        self._checkForSavePath()
        now = datetime.datetime.now()
        data = self._dataProvider.getAnlageVData_1_to_8(self._whg_id, self._vj)
        """
        data:
        {
            'name': 'Kendel', 
            'vorname': 'Martin', 
            'steuernummer': '222/333/44444', 
            'strasse': 'Mendelstr. 24', 
            'plz': '90429', 
            'ort': 'Nürnberg', 
            'whg_bez': '3. OG rechts', 
            'qm': '53', 
            'angeschafft_am': '1989-02-13', 
            'einhwert_az': 'ewewew ', 
            'fewontzg': 'N', 
            'isverwandt': 'N'
        }
        """
        self._wohnungIdent = ''.join((data['plz'], ' ', data['ort'],
                                      ', ', data['strasse'], ' / ', data['whg_bez']))
        self._stammdaten = data

        logfile = self._savePath + "/log_" + \
                  ''.join((data['plz'], '_', data['ort'],
                           '_', data['strasse'], '_',
                           data['whg_bez'])) + \
                  ".txt"

        self._log = open(logfile, 'w')
        self._writeLog('Starte Verarbeitung um ' + str(now))

        self._xdatadict['vj'] = self._vj
        self._xdatadict['zeilen'] = dict()

        self._getZeile_1_to_8()
        self._getZeile_9_to_14_mtlEinn()
        self._sectionWerbungskosten()
        self._getZeile_23_24_ueberschuss_zurechnung()
        self._writeInterface()

        now = datetime.datetime.now()
        self._writeLog('\n\nBeende Verarbeitung um ' + str(now))
        self._log.close()

    def _writeLog(self, txt: str) -> None:
        txt = ''.join((txt, '\n'))
        self._log.write(txt)

    def _writeInterface(self) -> None:
        jsonfile = self._savePath + "/anlagevdata_" + str(self._vj) + ".json"
        f = open(jsonfile, 'w')
        json.dump(self._xdatadict, f, indent=4)
        #f.write(x)
        f.close()

    def _writeRechnungenLog(self, rg: dict) -> None:
        """
        rg:
            {
                'rg_id': '48',
                'rg_datum': '30.08.2019',
                'rg_nr': 'BBB222',
                'betrag': '222.00',
                'verteilung_jahre': '1',
                'firma': 'zweierle',
                'bemerkung': 'fjsdlfdsjklfsdjil',
                'rg_bezahlt_am': '02.09.2019',
                'year_bezahlt_am': '2019',
                'voll_abzugsfaehig': True,
                'anteiliger_betrag': 222.00
            }
        """
        txt = ''.join(('\tFirma ', rg['firma'], ', Rg.Nr. ',
                        rg['rg_nr'], ' vom ', rg['rg_datum'], ', Betrag ', rg['betrag'],
                       '\n\t\tBezahlt am ', rg['rg_bezahlt_am'],
                       ', zu verteilen auf ', rg['verteilung_jahre'], ' Jahr(e). ',
                       '\n\t\tAnzusetzender Betrag: ', str(rg['anteiliger_betrag'])))
        self._writeLog(txt)


    def _getZeile_1_to_8(self):
        data = self._stammdaten
        """
        data:
        {
            'name': 'Kendel', 
            'vorname': 'Martin', 
            'steuernummer': '222/333/44444', 
            'strasse': 'Mendelstr. 24', 
            'plz': '90429', 
            'ort': 'Nürnberg', 
            'whg_bez': '3. OG rechts', 
            'qm': '53', 
            'angeschafft_am': '1989-02-13', 
            'einhwert_az': 'ewewew ', 
            'fewontzg': 'N', 
            'isverwandt': 'N'
        }
        """

        self._createZeile(1, ('Name', data['name']))
        self._createZeile(2, ('Vorname', data['vorname']))
        self._createZeile(3, ('Steuernummer', data['steuernummer']),
                             ('lfd. Nr.', self._anlage_nr))
        self._createZeile(4, ('Straße, Hausnummer', data['strasse']),
                             ('Angeschafft am', data['angeschafft_am']))
        self._createZeile(5, ('Postleitzahl', data['plz']), ('Ort', data['ort']))
        self._createZeile(6, ('Einheitswert-Aktenzeichen', data['einhwert_az']))
        self._createZeile(7, ('Als Ferienwohnung genutzt', data['fewontzg']),
                             ('An Angehörige vermietet', data['isverwandt']))
        self._createZeile(8, ('Gesamtwohnfläche', data['qm']))

    def _getZeile_9_to_14_mtlEinn(self) -> None:
        data: List[Dict[str, str]] = self._dataProvider.\
                getAnlageVData_9_to_14_mtlEinn(self._whg_id, self._vj)
        """
        data: list of dictionaries, order by gueltig_ab ascending
        [
            {
                'mea_id': '3', 
                'gueltig_ab': '2017-08-01', 
                'gueltig_bis': '2018-09-30', 
                'netto_miete': '310.00', 
                'nk_abschlag': '20.00'
            },
            {
                'mea_id': '4', 
                'gueltig_ab': '2018-10-01', 
                'gueltig_bis': '2019-05-31', 
                'netto_miete': '320.00', 
                'nk_abschlag': '25.00'
            }, 
            ...
        ]
        """
        #count the number of months to be considered in each dictionary
        #and multiply them by netto_miete and nk_abschlag adjustments:
        netto_miete = nk_abschlag = 0
        for d in data:
            cnt = datehelper.getNumberOfMonths(d['gueltig_ab'], d['gueltig_bis'], self._vj)
            netto_miete += (float(d['netto_miete']) * cnt) #Zeile 9
            nk_abschlag += (float(d['nk_abschlag']) * cnt) #Zeile 13

        #Grundsteuer: wird ignoriert, da sie ein durchlaufender Posten ist

        #get nebenkosten adjustment of last vj
        nkAdjustList: List[Dict[str, str]] = self._dataProvider. \
            getAnlageVData_13_nkKorr(self._whg_id, self._vj)
        """
        nkAdjustList: list of dictionaries:
            [
                {
                    'sea_id': '11', 
                    'vj': '2018', 
                    'betrag': '93.00', 
                    'art_id': '3', 
                    'art': 'Nebenkostennachzahlung (Mieter->Verm.)',
                    'ein_aus': 'e'
                }
            ]
        """
        adjustment = 0
        for adjust in nkAdjustList:
            betrag = float(adjust['betrag'])
            if adjust['ein_aus'] == 'a': betrag *= -1
            adjustment += betrag

        nk_eff = nk_abschlag + adjustment
        einnahme = round(netto_miete + nk_eff) #Zeile 21

        self._createZeile(9, ('Mieteinnahmen ohne Umlagen', round(netto_miete)))
        self._createZeile(13, ('Umlagen, verrechnet mit Erstattungen', round(nk_eff)))
        self._createZeile(21, ('Summe der Einnahmen', einnahme))
        self._summe_einnahmen = einnahme

    def _sectionWerbungskosten(self):
        self._getZeile_33_to_35_afa()
        self._getZeile_39_to_45_erhaltung()
        self._getZeile_47_verwaltkosten()
        self._getZeile_49_sonstiges()
        self._getZeile_22_und_50_summe_wk()

    def _getZeile_33_to_35_afa(self):
        afa = self._dataProvider.getAfa(self._whg_id, self._vj)
        """
        afa: 
        {
            'afa_id': '2', 
            'vj_ab': '2018', 
            'betrag': '343', 
            'prozent': '2.23', 
            'lin_deg_knz': 'l', 
            'afa_wie_vorjahr': 'Ja', 
            'art_afa': 'linear',
            'verwaltkosten': 200
        } 
        """
        afa_art = 'linear' if afa['lin_deg_knz'] == 'l' else 'degressiv'
        linear = 'X' if afa['lin_deg_knz'] == 'l' else ' '
        degressiv = ' ' if linear == 'X' else 'X'
        wie_vj = 'X' if afa['afa_wie_vorjahr'] == 'Ja' else ' '
        self._createZeile(33,
                          ('linear', linear),
                          ('degressiv', degressiv),
                          ('prozent', afa['prozent']),
                          ('wie_vorjahr', wie_vj),
                          ('betrag', afa['betrag']))

        self._summe_wk += int(afa['betrag'])

        #todo: createZeile 34, 35

    def _getZeile_36_to_37_kredit(self) -> None:
        #todo
        pass

    def _getZeile_38_renten(self) -> None:
        #todo
        pass

    def _getZeile_39_to_45_erhaltung(self) -> None:
        # eigenen Absatz für die als Nachweis
        # benötigten Rechnungen im Log schreiben:
        self._writeLog(''.join(('>>>> ', self._wohnungIdent, ' <<<<')))
        txt = "\nFolgende Rechnungen werden zum Nachweis benötigt:\n"
        self._writeLog(txt)

        #die für dieses Vj relevanten Rechnungen finden:
        rgfilter = RechnungFilter(self._whg_id, self._vj, self._dataProvider)
        rgfilter.registerCallback(self._writeRechnungenLog)
        aufwaende: XErhaltungsaufwand = rgfilter.getErhaltungsaufwaende()
        # die notwendigen Einträge in die Schnittstellendatei machen:
        self._createZeile(39, ('voll_abzuziehende',
                               round(aufwaende.voll_abzuziehen)))
        self._summe_wk += aufwaende.voll_abzuziehen

        z = 41 #erste Zeile für zu verteilende Erhalt.Aufwendungen
        # in Zeile 41 kommt der Gesamtaufwand des Vj und der Anteil für das Vj:
        self._createZeile(z,
                          ('gesamtaufwand_vj', round(aufwaende.vj_gesamtaufwand)),
                          ('anteil_vj', round(aufwaende.abzuziehen_vj)))
        self._summe_wk += aufwaende.abzuziehen_vj

        z += 1 # in die nächste Zeile (42) kommt der Anteil für Vj - 4 Jahre
        for y in range(4, 0, -1):
            ident = ''.join(('vj_minus_', str(y)))
            aufwand = aufwaende.get_abzuziehen_aus_vj_minus(y)
            self._createZeile(z, (ident, round(aufwand)))
            self._summe_wk += aufwand
            z += 1

    def _getZeile_47_verwaltkosten(self) -> None:
        vwkost: int = self._dataProvider.\
                getAnlageVData_47_verwaltkosten(self._whg_id, self._vj)
        self._createZeile(47, ('verwaltungskosten', vwkost))
        self._summe_wk += vwkost

    def _getZeile_49_sonstiges(self) -> None:
        sonstige: int = self._dataProvider.\
            getAnlageVData_49_sonstiges(self._whg_id, self._vj)
        self._createZeile(49, ('sonstige', sonstige))
        self._summe_wk += sonstige

    def _getZeile_22_und_50_summe_wk(self) -> None:
        summe_wk = round(self._summe_wk)
        self._createZeile(22, ('summe_werbungskosten', summe_wk))
        self._createZeile(50, ('summe_werbungskosten', summe_wk))

    def _getZeile_23_24_ueberschuss_zurechnung(self) -> None:
        ueberschuss = round(self._summe_einnahmen - self._summe_wk)
        self._createZeile(23, ('ueberschuss', ueberschuss))

        zurechng_mann, zurechng_frau = \
            self._dataProvider.getAnlageVData_24_zurechnung(self._whg_id) # prozentsätze
        betrag_mann = int(zurechng_mann)/100 * ueberschuss
        betrag_frau = ueberschuss - betrag_mann
        self._createZeile(24, ('zurechng_mann', round(betrag_mann)),
                              ('zurechng_frau', round(betrag_frau)))

    def _createZeile(self, nr: int, *args):
        """
        create a dictionary representing the fields in a Zeile of Anlage V
        :param args: each arg is a list containing a key (field's name)
                     and a value (field's value)
                     e.g. ('Straße, Hausnummer', 'Mendelstr. 24')
        :return: dict:
            {
                "zeile": 4,
                "felder": [
                    {
                        "name": "Straße, Hausnummer",
                        "value": "Mendelstr. 24"
                    },
                    {
                        "name": "Angeschafft am",
                        "value": "13.05.1997"
                    }
                ]
            }
        """
        feldlist = list()
        for item in args:
            d = dict()
            d['name'] = item[0]
            d['value'] = str(item[1])
            feldlist.append(d)

        self._xdatadict['zeilen'][nr] = feldlist

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class RechnungFilter:
    def __init__(self, whg_id: int, vj: int, dataprovider: DataProvider):
        self._whg_id = whg_id
        self._vj = vj
        self._dataprovider = dataprovider
        self._callback = None

    def registerCallback(self, cb) -> None:
        # the function to register has to accept a dictionary
        # (representing a rechnung)
        self._callback = cb

    def getErhaltungsaufwaende(self):
        rechnungen: List[Dict[str, str]] = self._dataprovider.getRechnungsUebersicht(self._whg_id)
        """
        rechnungen: list of dictionaries: 
            {
                'rg_id': '48', 
                'rg_datum': '30.08.2019', 
                'rg_nr': 'BBB222', 
                'betrag': '222.00',
                'verteilung_jahre': '1', 
                'firma': 'zweierle', 
                'bemerkung': 'fjsdlfdsjklfsdjil',
                'rg_bezahlt_am': '02.09.2019',
                'year_bezahlt_am': '2019'
            }
        """
        aufwand = XErhaltungsaufwand()
        for rg in rechnungen:
            year_bezahlt_am = int(rg['year_bezahlt_am'])
            if not rg['year_bezahlt_am']: #Rechnung noch nicht bezahlt
                pass
            elif year_bezahlt_am > self._vj:
                #Rechnung noch nicht relevant, erst nach dem Vj bezahlt
                pass
            elif year_bezahlt_am + int(rg['verteilung_jahre']) <= self._vj:
                # Rechnung nicht mehr relevant - schon im Vor-Vj bezahlt oder
                # fertig abgeschrieben
                pass
            else:
                #in diesen Zweig läuft alles, was berücksichtigt werden soll,
                #entweder 'voll_abzuziehen' im Vj oder anteilig
                betrag = float(rg['betrag'])
                verteilung_jahre = int(rg['verteilung_jahre'])
                if year_bezahlt_am == self._vj and verteilung_jahre == 1:
                    aufwand.voll_abzuziehen += betrag
                    self._doCallback(rg, True, betrag)
                elif verteilung_jahre > 1:
                    # Versorgung der Zeilen 41 bis 45
                    if year_bezahlt_am == self._vj:
                        aufwand.vj_gesamtaufwand += betrag
                    anteil = betrag / verteilung_jahre
                    years = self._vj - year_bezahlt_am
                    aufwand.addto_abzuziehen_aus_vj_minus(years, anteil)
                    self._doCallback(rg, False, anteil)
        aufwand.roundAufwaende()
        return aufwand

    def _doCallback(self, rg: dict, vollAbz: bool, betrag: float):
        if self._callback:
            rg['voll_abzugsfaehig'] = vollAbz
            rg['anteiliger_betrag'] = betrag
            self._callback(rg)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rechnungfiltercallback(rg: dict):
    print("logge: ", rg)

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    avdata = AnlageVData(1, 2, 2018, dp)
    avdata.startWork()

    # filter = RechnungFilter(1, 2018, dp)
    # filter.registerCallback(rechnungfiltercallback)
    # betraege: dict = filter.getBetraege()
    # print(betraege)

if __name__ == '__main__':
    test()