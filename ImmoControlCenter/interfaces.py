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

    def equals( self, other ) -> bool:
        return True if self.__dict__ == other.__dict__ else False


#################################################################
def setFromDict( object, valuedict:Dict ):
    d = object.__dict__
    for k, v in valuedict.items():
        d[k] = v

#######################  Mietverhältnis  ########################
# class XMietverhaeltnis:
#     def __init__( self, valuedict:Dict=None ):
#         self.id = 0
#         self.mv_id = ""
#         self.mobj_id = ""
#         self.von = ""
#         self.bis = ""
#         self.name = ""
#         self.vorname = ""
#         self.telefon = ""
#         self.mobil = ""
#         self.mailto = ""
#         self.anzahl_pers = 1
#         self.bemerkung1 = ""
#         self.bemerkung2 = ""
#         self.kaution = 0
#         self.kaution_bezahlt_am = ""
#         if valuedict:
#             setFromDict( self, valuedict )

#################  Mietobjekt  #############################
class XMietobjektExt( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        ### zuerst die Master-Daten ###
        self.master_id:int = 0 # ID des Master-Objekts (Tabelle masterobjekt)
        self.master_name:str = ""
        self.strasse_hnr:str = ""
        self.plz:str = ""
        self.ort:str = ""
        self.gesamt_wfl:int = 0
        self.anz_whg:int = 0
        self.veraeussert_am:str = ""
        self.hauswart:str = ""
        self.hauswart_telefon:str = ""
        self.hauswart_mailto:str = ""
        self.bemerkung_masterobjekt:str = "" ### ACHTUNG: Dieses Feld heißt in der Tabelle masterobjekt "bemerkung" --
                                                # Beim Select berücksichtigen!
        ### dann die Daten des Mietobjekts, das ausgesucht wurde
        self.mobj_id:str = "" # ID des Mietobjekts (Tabelle mietobjekt)
        self.whg_bez:str = ""
        self.qm:int = 0  # Größe der Wohnung -- ist identisch mit gesamt_wfl, wenn es sich beim Masterobjekt nicht um ein
                         # ganzes Haus handelt
        self.container_nr:str = "" # Nummer des zur Wohnung gehörenden Abfallcontainers
        self.bemerkung_mietobjekt:str = "" ### ACHTUNG: Dieses Feld heißt in der Tabelle mietobjekt "bemerkung" --
                                            # Beim Select berücksichtigen!
        # Ergänzende Daten zu Mieter, Miete, NKV, Verwaltung und HGV
        self.mieter:str = ""
        self.telefon_mieter:str = ""
        self.mailto_mieter:str = ""
        self.nettomiete:float = 0.0
        self.nkv:float = 0.0
        self.kaution:float = 0.0
        self.weg_name:str = ""
        self.verwalter:str = ""
        self.hgv_netto:float = 0.0
        self.ruezufue:float = 0.0
        self.hgv_brutto:float = 0.0
        if valuedict:
            self.setFromDict( valuedict )

#######################  Geschäftsreise  #######################
class XGeschaeftsreise( XBase ):
    def __init__( self, valuedict:Dict=None ):
        self.id = 0
        self.mobj_id = ""
        self.jahr = 0
        self.von = ""
        self.bis = ""
        self.ziel = ""
        self.zweck = ""
        self.km = 0
        self.verpfleg_pauschale = 0.0
        self.uebernachtung = ""
        self.uebernacht_kosten = 0.0
        if valuedict:
            setFromDict( self, valuedict )

####################### Wertebereich ##########################
class XWertebereich:
    def __init__(self, valuedict:Dict=None):
        self.id = 0
        self.table_name = ""
        self.column_name = ""
        self.isNumeric = 0
        self.wert = None
        self.beschreibung_kurz = ""
        self.beschreibung = ""
        if valuedict:
            setFromDict( self, valuedict )

####################### Zahlung #################################1
class XZahlung( XBase ):
    def __init__( self, valuedict:Dict=None ):
        XBase.__init__( self )
        self.z_id:int = 0
        self.master_id:int = 0 # ID des Master-Objekts (Tabelle masterobjekt)
        self.mobj_id:str = "" # ID des Mietobjekts (Tabelle mietobjekt) --- kann frei sein, dann muss aber master_id versorgt sein
            # GENAU einer der nachfolgenden 4 IDs muss versorgt sein
        self.meinaus_id:int = 0 # ID der monatlichen Einzahlung (Tabelle mtleinaus)
        self.saus_id:int = 0 # ID der sonstigen Auszahlung (Tabelle sonstaus)
        self.kreditor:str = ""
        self.nka_id:int = 0  # ID der Nebenkostenabrechnung (Tabelle nkabrechng)
        self.hga_id:int = 0  # ID der Hausgeld-Abrechnung (Tabelle hgabrechng)
        self.write_time:str = ""  # Zeitpunkt der Anlage dieses Satzes
        self.jahr:int = 0 # Veranlagungsjahr
        self.monat:str = ""  # auf welchen Monat sich die Zahlung bezieht (nur für Miete und HGV relevant)
        self.betrag:float = 0.0
        self.zahl_art:str = ""  # {'brutto_miete', 'nka', 'hgv', 'hga', 'rechng'}
        self.kostenart:str = "" # {s, v, a, r, sam, g }
        self.umlegbar:bool = False
        self.buchungsdatum:str = ""
        self.buchungstext:str = ""
        if valuedict:
            self.setFromDict( valuedict )

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

class XZahlung3:
    def __init__( self, valuedict:Dict=None ):
        self.z_id: int = 0
        self.master_name: str = ""
        self.mobj_id: str = ""  # ID des Mietobjekts (Tabelle mietobjekt)
        self.saus_id: int = 0  # ID der sonstigen Auszahlung (Tabelle sonstaus)
        self.kreditor: str = ""
        self.betrag: float = 0.0
        self.buchungsdatum:str = ""
        self.buchungstext:str = "" # aus Tabelle sonstaus
        self.kostenart:str = ""
        self.zahl_art:str = ""
        self.art: str = ""  # Kombination aus zahl_art und kostenart
                            # {'brutto_miete', 'nka', 'hgv', 'hga', 'a', 'g', 'r',...}
        if valuedict:
            setFromDict( self, valuedict )

###################  Mietverhältnis  #########################
class XMietverhaeltnis( XBase ):
    def __init__( self, valuedict:Dict=None ):
        self.id = 0
        self.mv_id = ""
        self.mobj_id = ""
        self.von = ""
        self.bis = ""
        self.name = ""
        self.vorname = ""
        self.name2 = ""
        self.vorname2 = ""
        self.telefon = ""
        self.mobil = ""
        self.mailto = ""
        self.anzahl_pers = 1
        self.IBAN = ""
        self.nettomiete = 0.0
        self.nkv = 0.0
        self.kaution = 0
        self.kaution_bezahlt_am = ""
        self.bemerkung1 = ""
        self.bemerkung2 = ""
        if valuedict:
            self.setFromDict( valuedict )

#################### Kostenart ###################################

class XKostenart:
    def __init__( self, kostenart_kurz="", kostenart_lang="", beschreibung="" ):
        self.kostenart_kurz = kostenart_kurz
        self.kostenart_lang = kostenart_lang
        self.beschreibung = beschreibung

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
        self.kostenart: str = ""  # Kostenart-Kürzel aus Tabelle sonstaus
        self.kostenart_lang = ""  # Langtext für das Kostenart-Kürzel
        if valuedict:
            setFromDict( self, valuedict )

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
    kostenart:str = ""
    kostenart_lang:str = ""
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
        self.davon_reparaturen = 0
        self.ueberschuss_o_afa = 0
        self.ertrag_pro_qm = 0.0
        self.ertrag_pro_qm_ohne_rep = 0.0
        self.afa = 0
        self.ueberschuss_m_afa = 0

class XAusgabe:
    def __init__(self):
        self.master_name = ""
        self.mobj_id = ""
        self.kreditor = ""
        self.betrag = 0.0
        self.buchungsdatum = ""
        self.kostenart = ""
        self.buchungstext = ""

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

def testCompare():
    mv1 = XMietverhaeltnis()
    mv2 = XMietverhaeltnis()
    # mv2.mv_id = 22
    # mv1.mv_id = 22
    print( "Gleich" if mv2.equals( mv1) else "Nicht gleich" )
    print( "Gleich" if mv2 == mv1 else "Nicht gleich" )  # SO kann man 2 Objekte nicht vergleichen!!

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
    #test()
    testCompare()