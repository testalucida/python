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
    def __init__(self, whg_id: int, vj: int, dataprovider: DataProvider):
        self._whg_id = whg_id
        self._vj = vj
        self._xdata = dict() #Dictionary für die Schnittstellendaten
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
        self._getZeile_1_to_8()
        self._getZeile_9_to_14_mtlEinn()
        self._getAfa()

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
        json.dump(self._xdata, f)
        #f.write(x)
        f.close()

    def _getZeile_1_to_8(self):
        data = self._dataProvider.getAnlageVData_1_to_8(self._whg_id, self._vj)
        """
        data:
        {
            'name': 'Kendel', 
            'vorname': 'Martin', 
            'steuernummer': '217/235/50499', 
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
        self._addItems(data)

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
        ]
        """
        #count the number of months to be considered in each dictionary
        #and multiply them by netto_miete and nk_abschlag
        netto_miete = nk_abschlag = 0
        for d in data:
            cnt = datehelper.getNumberOfMonths(d['gueltig_ab'], d['gueltig_bis'], self._vj)
            netto_miete += (float(d['netto_miete']) * cnt) #Zeile 9
            nk_abschlag += (float(d['nk_abschlag']) * cnt) #Zeile 13

        einnahme = netto_miete + nk_abschlag #Zeile 21
        data = {
            'netto_miete': netto_miete,
            'nk_abschlag': nk_abschlag,
            'summe_einnahmen': einnahme
        }
        self._addItems(data)

    def _getAfa(self):
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
        self._addItems(afa)

    def _addItems(self, data: dict):
        for k, v in data.items():
            self._xdata[k] = v

def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    avdata = AnlageVData(1, 2018, dp)
    avdata.startWork()

if __name__ == '__main__':
    test()