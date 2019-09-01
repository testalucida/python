import json
import datetime
from business import DataProvider
import datehelper

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
        self._zeilenlist = list() #liste der Zeilen,
                                  # die dem Schnittstellendict. hinzugefügt wird
        self._dataProvider = dataprovider
        self._savePath = '/home/martin/Projects/python/Wohnungsverwaltung'
        self._log = None

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
        logfile = self._savePath + "/log_" + str(now) + ".txt"
        self._log = open(logfile, 'w')
        self._writeLog('Starte Verarbeitung um ' + str(now))

        self._xdatadict['vj'] = self._vj
        self._xdatadict['zeilen'] = self._zeilenlist

        self._getZeile_1_to_8()
        self._getZeile_9_to_14_mtlEinn()
        self._sectionWerbungskosten()

        self._writeInterface()

        now = datetime.datetime.now()
        self._writeLog('Beende Verarbeitung um ' + str(now))
        self._log.close()

    def _writeLog(self, txt: str) -> None:
        txt = ''.join((txt, '\n'))
        self._log.write(txt)

    def _writeInterface(self) -> None:
        jsonfile = self._savePath + "/anlagevdata_" + str(self._vj) + ".json"
        f = open(jsonfile, 'w')
        json.dump(self._xdatadict, f)
        #f.write(x)
        f.close()

    def _getZeile_1_to_8(self):
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
        data = self._dataProvider.\
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
        nkAdjustList = self._dataProvider. \
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

        einnahme = netto_miete + nk_abschlag #Zeile 21
        nk_eff = nk_abschlag + adjustment

        self._createZeile(9, ('Mieteinnahmen ohne Umlagen', netto_miete))
        z13 = self._createZeile(13, ('Umlagen, verrechnet mit Erstattungen', nk_eff))
        z13['nk_abschlag'] = nk_abschlag
        z13['nk_korrektur'] = adjustment
        self._createZeile(21, ('Summe der Einnahmen', einnahme))

    def _sectionWerbungskosten(self):
        self._getZeile_33_to_35_afa()

    def _getZeile_33_to_35_afa(self):
        afa = self._dataProvider.getAfaData(self._whg_id, self._vj)
        """
        afa: 
        {
            'afa_id': '2', 
            'vj_ab': '2018', 
            'betrag': '343', 
            'prozent': '2.23', 
            'lin_deg_knz': 'l', 
            'afa_wie_vorjahr': 'Ja', 
            'art_afa': 'linear'
        } 
        """
        afa_art = 'linear' if afa['lin_deg_knz'] == 'l' else 'degressiv'
        wie_vj = 'X' if afa['afa_wie_vorjahr'] == 'Ja' else ' '
        self._createZeile(33,
                          (afa_art, 'X'),
                          ('prozent', afa['prozent']),
                          ('wie_vorjahr', wie_vj),
                          ('betrag', afa['betrag']))

    def _getZeile_36_to_37_afa(self) -> None:
        #todo: start from here after vacancies
        pass

    def _getZeile_47_mtlVerwaltkosten(self) -> None:
        data = self._dataProvider.\
                getAnlageVData_47_mtlVerwaltkosten(self._whg_id, self._vj)
        """
        data: list of dictionaries, order by gueltig_ab ascending
        [
            {
                'mea_id': '3', 
                'gueltig_ab': '2017-08-01', 
                'gueltig_bis': '2018-09-30', 
                'hg_netto_abschlag': '310.00', 
                'ruecklage_zufuehr': '20.00'
            },
            {
                'mea_id': '3', 
                'gueltig_ab': '2017-08-01', 
                'gueltig_bis': '2018-09-30', 
                'hg_netto_abschlag': '310.00', 
                'ruecklage_zufuehr': '20.00'
            },
            ... 
        ]
        
        ruecklage_zufuehr wird im Rahmen der ESt nicht benötigt, aber an 
        anderer Stelle für die Renditeberechnung.
        """
        #count the number of months to be considered in each dictionary
        #and multiply them by netto_miete and nk_abschlag
        hg_netto_abschlag = 0
        for d in data:
            cnt = datehelper.getNumberOfMonths(d['gueltig_ab'], d['gueltig_bis'], self._vj)
            hg_netto_abschlag += (float(d['netto_miete']) * cnt) #Zeile 47

        data = {
            'hg_netto_abschlag': hg_netto_abschlag
        }
        self._addItems(data)

    def _addItems(self, data: dict):
        for k, v in data.items():
            self._xdatadict[k] = v

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
        zeile = dict()
        zeile['zeile'] = nr
        feldlist = list()
        for item in args:
            d = dict()
            d['name'] = item[0]
            d['value'] = item[1]
            feldlist.append(d)

        zeile['felder'] = feldlist
        #add zeile to interface dictionary, key 'zeilen'
        self._zeilenlist.append(zeile)
        return zeile

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    avdata = AnlageVData(1, 2, 2018, dp)
    avdata.startWork()

if __name__ == '__main__':
    test()