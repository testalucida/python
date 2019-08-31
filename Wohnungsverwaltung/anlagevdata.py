import json
import datetime
from business import DataProvider
import datehelper

class AnlageVData:
    """
    Sammelt alle Daten, die zur Erstellung der Anlage V für eine Wohnung
    für ein Veranlagungsjahr benötigt werden.
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
        self._getAfa()

        now = datetime.datetime.now()
        self._writeLog('Beende Verarbeitung um ' + str(now))
        self._log.close()

    def _writeLog(self, txt: str) -> None:
        txt = ''.join((txt, '\n'))
        self._log.write(txt)

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