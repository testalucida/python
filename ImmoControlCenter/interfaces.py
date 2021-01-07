from typing import Dict

class XBase:
    def __init__( self, valuedict:Dict=None ):
        if valuedict:
            self.setFromDict( valuedict )

    def setFromDict( self, d: Dict ):
        _d = self.__dict__
        for k, v in d.items():
            _d[k] = v

class XZahlung:

    master_id:int = 0 # ID des Master-Objekts (Tabelle masterobjekt)
    mobj_id:str = "" # ID des Mietobjekts (Tabelle mietobjekt) --- kann frei sein, dann muss aber master_id versorgt sein
    # GENAU einer der nachfolgenden 4 IDs muss versorgt sein
    meinaus_id:int = 0 # ID der monatlichen Einzahlung (Tabelle mtleinaus)
    saus_id:int = 0 # ID der sonstigen Auszahlung (Tabelle sonstaus)
    nka_id:int = 0  # ID der Nebenkostenabrechnung (Tabelle nkabrechng)
    hga_id:int = 0  # ID der Hausgeld-Abrechnung (Tabelle hgabrechng)
    #---
    write_time:str = ""  # Zeitpunkt der Anlage dieses Satzes
    jahr:int = 0 # Veranlagungsjahr
    monat:str = ""  # auf welchen Monat sich die Zahlung bezieht (nur für Miete und HGV relevant)
    betrag:float = 0.0
    zahl_art:str = ""  # {'brutto_miete', 'nka', 'hgv', 'hga', 'rechng'}

class XSonstAus( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    saus_id:int = 0
    master_id:int = 0
    master_name:str = ""
    mobj_id:str = ""
    kreditor:str = ""
    rgnr:str = ""
    rgdatum:str = ""
    rgtext:str = ""  # der Text auf der Rechnung
    betrag:float = 0.0
    umlegbar:bool = False
    werterhaltend:bool = False
    buchungsdatum:str = ""
    buchungsjahr:int = 0
    buchungstext:str = "" # der Text auf dem Buchungsbeleg, der bei öfftl. Providern identifizierend ist. (Kundennummer, Vertragsnummer etc.)

class XSonstAusSummen( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    summe_aus:int = 0
    #summe_ein:int = 0
    summe_werterhaltend = 0
    #summe_nicht_werterhaltend = 0
    summe_umlegbar = 0
    #summe_nicht_umlegbar = 0

class XSollzahlung( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    mobj_id:str = ""
    von:str = ""
    bis:str = ""
    netto:float = 0.0  # Nettomiete bei Soll-Miete, Netto-HG (ohne rüzufü) bei HGV
    brutto:float = 0.0  # Summe aus netto und zusatz
    bemerkung:str = ""

class XSollHausgeld( XSollzahlung ):
    def __init__( self, valuedict:Dict=None ):
        XSollzahlung.__init__( self, valuedict )

    shg_id = 0
    vw_id = ""
    vwg_id = 0
    weg_name = ""
    ruezufue:float = 0.0

class XSollMiete( XSollzahlung ):
    def __init__( self, valuedict:Dict=None ):
        XSollzahlung.__init__( self, valuedict )

    sm_id = 0
    mv_id = ""
    nkv:float = 0.0


def printX( x:XSonstAus ):
    print( x )
    d = x.__dict__
    for k, v in d.items():
        print( k, ": ", v )

def test():
    x = XSonstAus()
    x.saus_id = 1
    x.kreditor = "K. Frantz"
    x.master_id = 11
    x.mobj_id = "kleist_01"
    printX( x )

    x2 = XSonstAus()
    d = {
        "saus_id": 20,
        "master_id": "HOM_Remigius",
        "mobj_id": "remigius",
        "kreditor": "Aloysius",
        "rgnr": "ABC2020_6t543",
        "rgdatum": "2020-10-31",
        "betrag": 546.78
    }
    x2.setFromDict( d )
    printX( x2 )

    print( "---------------------------" )
    x3 = XSonstAus( d )
    printX( x3 )

if __name__ == "__main__":
    test()