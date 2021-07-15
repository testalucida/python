from abc import abstractmethod
from typing import Dict

class XBase:
    def __init__( self, valuedict:Dict=None ):
        if valuedict:
            self.setFromDict( valuedict )

    def setFromDict( self, d: Dict ):
        _d = self.__dict__
        for k, v in d.items():
            _d[k] = v

#################################################################
def setFromDict( object, valuedict:Dict ):
    d = object.__dict__
    for k, v in valuedict.items():
        d[k] = v

#######################  Mietverhältnis  ########################
class XMietverhaeltnis:
    def __init__( self, valuedict:Dict=None ):
        self.id = 0
        self.mv_id = ""
        self.mobj_id = ""
        self.von = ""
        self.bis = ""
        self.name = ""
        self.vorname = ""
        self.telefon = ""
        self.mobil = ""
        self.mailto = ""
        self.anzahl_pers = 1
        self.bemerkung1 = ""
        self.bemerkung2 = ""
        self.kaution = 0
        self.kaution_bezahlt_am = ""
        if valuedict:
            setFromDict( self, valuedict )



####################### Zahlung #################################1
class XZahlung:
    z_id:int = 0
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

class XZahlung2:
    def __init__( self, valuedict:Dict=None ):
        self.z_id: int = 0
        self.master_name: str = ""
        self.mobj_id: str = ""  # ID des Mietobjekts (Tabelle mietobjekt)
        # GENAU einer der nachfolgenden 4 IDs muss versorgt sein
        self.meinaus_id: int = 0  # ID der monatlichen Einzahlung (Tabelle mtleinaus)
        self.saus_id: int = 0  # ID der sonstigen Auszahlung (Tabelle sonstaus)
        self.nka_id: int = 0  # ID der Nebenkostenabrechnung (Tabelle nkabrechng)
        self.hga_id: int = 0  # ID der Hausgeld-Abrechnung (Tabelle hgabrechng)
        self.jahr: int = 0  # Veranlagungsjahr
        self.betrag: float = 0.0
        self.zahl_art: str = ""  # {'brutto_miete', 'nka', 'hgv', 'hga', 'rechng'}
        self.qm:int = 0
        self.gesamt_wfl:int = 0
        self.afa:int = 0
        if valuedict:
            setFromDict( self, valuedict )


#################### SonstAus  ###################################

class XSonstAus:
    def __init__( self, valuedict: Dict = None ):
        self.saus_id: int = 0
        self.master_id: int = 0
        self.master_name: str = ""
        self.mobj_id: str = ""
        self.kostenart:str = ""
        self.kreditor: str = ""
        self.rgnr: str = ""
        self.rgdatum: str = ""
        self.rgtext: str = ""  # der Text auf der Rechnung
        self.betrag: float = 0.0
        self.umlegbar: bool = False
        self.werterhaltend: bool = False
        self.buchungsdatum: str = ""
        self.buchungsjahr: int = 0
        self.buchungstext: str = ""  # der Text auf dem Buchungsbeleg, der bei öfftl. Providern identifizierend ist. (Kundennummer, Vertragsnummer etc.)
        if valuedict:
            setFromDict( self, valuedict )

# class XSonstAus( XBase ):
#     def __init__( self, valuedict:Dict=None ):
#         XBase.__init__( self, valuedict )
#
#     saus_id:int = 0
#     master_id:int = 0
#     master_name:str = ""
#     mobj_id:str = ""
#     kreditor:str = ""
#     rgnr:str = ""
#     rgdatum:str = ""
#     rgtext:str = ""  # der Text auf der Rechnung
#     betrag:float = 0.0
#     umlegbar:bool = False
#     werterhaltend:bool = False
#     buchungsdatum:str = ""
#     buchungsjahr:int = 0
#     buchungstext:str = "" # der Text auf dem Buchungsbeleg, der bei öfftl. Providern identifizierend ist. (Kundennummer, Vertragsnummer etc.)
#

#################### Abrechnung ##################################
class XAbrechnung:
    def __init__( self ):
        self.mobj_id = ""
        self.von = ""
        self.bis = ""
        self.ab_jahr = 0
        self.betrag = 0.0
        self.ab_datum = ""
        self.buchungsdatum = ""
        self.bemerkung = ""
        self.deleteFlag = False

    def getName( self ) -> str:
        pass

    def getId( self ) -> int:
        pass

class XNkAbrechnung( XAbrechnung ):
    def __init__( self ):
        XAbrechnung.__init__( self )
        self.nka_id = 0
        self.mv_id = ""

    def getName( self ) -> str:
        return self.mv_id

    def getId( self ) -> int:
        return self.nka_id

class XHgAbrechnung( XAbrechnung ):
    def __init__( self ):
        XAbrechnung.__init__( self )
        self.hga_id = 0
        self.vwg_id = 0
        self.weg_name_vw_id = ""

    def getName( self ) -> str:
        return self.weg_name_vw_id

    def getId( self ) -> int:
        return self.hga_id

##################### SonstAusSummen ###################################
class XSonstAusSummen( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    summe_aus:int = 0
    #summe_ein:int = 0
    summe_werterhaltend = 0
    #summe_nicht_werterhaltend = 0
    summe_umlegbar = 0
    #summe_nicht_umlegbar = 0

class XBuchungstextMatch( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self, valuedict )

    master_id:int = 0
    master_name:str = ""
    mobj_id:str = ""
    kreditor:str = ""
    buchungstext:str = ""
    umlegbar:int = 0

class XSollzahlung:
    def __init__( self ):
        self.mobj_id:str = ""
        self.von:str = ""
        self.bis:str = ""
        self.netto:float = 0.0  # Nettomiete bei Soll-Miete, Netto-HG (ohne rüzufü) bei HGV
        self.brutto:float = 0.0  # Summe aus netto und zusatz
        self.bemerkung:str = ""

    @abstractmethod
    def getId( self ) -> int:
        pass

    @abstractmethod
    def setId( self, value:int ) -> None:
        pass

class XSollHausgeld( XSollzahlung ):
    def __init__( self, valuedict:Dict=None ):
        XSollzahlung.__init__( self )
        self.shg_id = 0
        self.vw_id = ""
        self.vwg_id = 0
        self.weg_name = ""
        self.ruezufue:float = 0.0
        if ( valuedict ):
            setFromDict( self, valuedict )

    def getId( self ) -> int:
        return self.shg_id

    def setId( self, value: int ) -> None:
        self.shg_id = value

class XSollMiete( XSollzahlung ):
    def __init__( self, valuedict:Dict=None ):
        XSollzahlung.__init__( self )
        self.sm_id = 0
        self.mv_id = ""
        self.von = ""
        self.bis = ""
        self.netto = 0.0
        self.nkv:float = 0.0
        self.bemerkung = ""
        if( valuedict ):
            setFromDict( self, valuedict )

    def getId( self ) -> int:
        return self.sm_id

    def setId( self, value: int ) -> None:
        self.sm_id = value

class XOffenerPosten:
    def __init__( self, valuedict:Dict=None ):
        self.opos_id = 0
        self.debi_kredi = "" # Kreditor oder Debitor, der sich hinter der gefüllten o.a. ID verbirgt; oder Firma (Freitext)
        self.erfasst_am = ""
        self.betrag = 0.0 # kleiner 0: ich schulde ; > 0: mir steht zu
        self.betrag_beglichen = 0.0 # Teilbetrag von Betrag, der bereits beglichen ist
        self.letzte_buchung_am = "" # wann die letzte (Teil-) Buchung auf den offenen Betrag entrichtet wurde
        self.bemerkung = ""
        if valuedict:
            setFromDict( self, valuedict )

class XNotiz:
    def __init__(self, valuedict:Dict=None ):
        self.notiz_id = 0
        self.bezug = ""
        self.ueberschrift = ""
        self.text = ""
        self.erfasst_am = ""
        self.erledigt = 0
        self.lwa = ""
        if valuedict:
            setFromDict( self, valuedict )

class XRendite:
    def __init__( self ):
        self.master_name = ""
        self.wert = 0
        self.qm = 0
        self.jahr = 0
        self.einnahmen = 0
        self.ausgaben = 0
        self.ueberschuss_o_afa = 0
        self.afa = 0
        self.ueberschuss_m_afa = 0

class XKontoEintrag:
    mobj_id = ""         # Name des Objekts, z.B. ww224, ist Name des Kontos (der Tabelle)
    name = ""            # Name des Mieters oder des Verwalters
    id = 0
    z_id = 0 #Referenz auf z_id in Tabelle zahlung
    write_access = "" # Timestamp des letzten Schreibzugriffs
    forderungsdatum = "" # wann Betrag gefordert wurde. Rechnungsdatum, Datum der NK-Abrechng. etc.
    buchungsdatum = ""   # wann der geforderte Betrag auf dem ING-Diba-Konto gebucht wurde
    monat = 0            # betroffener Monat (z.B. Miete, HG-Vorauszahlung)
    jahr = 0             # dto
    betrag = 0.0
    art = ""             # {Bruttomiete|NKA|HGV|HGA|Rechng|Gebühr}
    bemerkung = ""


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