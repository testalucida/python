import json
from business import DataProvider

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
        afa = self._dataProvider.getAfaData(self._whg_id, self._vj)



def test():
    from business import DataProvider, DataError
    dp = DataProvider()
    dp.connect('martin', 'fuenf55')

    avdata = AnlageVData(1, 2018, dp)
    avdata.startWork()

if __name__ == '__main__':
    test()