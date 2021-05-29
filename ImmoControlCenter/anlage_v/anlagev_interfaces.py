from typing import Any, List, Dict

from interfaces import XBase, setFromDict


class XSteuerpflichtiger:
    def __init__( self ):
        self.name = "Kendel"
        self.vorname = "Martin"
        self.steuernummer = ""

class ZahlungsIntervall:
    def __init__(self):
        von:str = ""
        bis:str = ""
        anzMonate:int = 0
        netto:float = 0.0 # Netto-ME bzw. HG-netto
        zusatz:float = 0.0 # NKV bzw. RüZuFü

class XMieteinnahme:
    def __init__(self, master_name:str=""):
        self.master_name:str = master_name
        self.bruttoMiete:int = 0
        self.offnNkErstattg:int = 0
        self.nettoMiete:int = 0
        self.nkv:int = 0
        self.nka:int = 0
        self.nettoSoll:int = 0
        self.bemerkung:str = ""

class XAfA:
    def __init__(self, master_name:str="" ):
        self.master_name = master_name
        self.afa_linear: bool = False
        self.afa_degressiv: bool = False
        self.afa_prozent: float = 0.0
        self.afa_wie_vorjahr: bool = True
        self.afa: float = 0.0

class XAusgabeKurz:
    def __init__(self, valuedict:Dict=None):
        self.master_name = ""
        self.master_id = 0
        self.mobj_id = ""
        self.kostenart = ""
        self.kreditor = ""
        self.betrag = 0.0
        self.buchungstext = ""
        self.buchungsdatum = ""
        if valuedict:
            setFromDict( self, valuedict )

class XAufwandVerteilt:
    def __init__(self, master_name:str="" ):
        self.master_name = master_name
        self.gesamt_aufwand_vj:int = 0
        self.aufwand_vj:int = 0
        self.aufwand_vj_minus_4: int = 0
        self.aufwand_vj_minus_3: int = 0
        self.aufwand_vj_minus_2: int = 0
        self.aufwand_vj_minus_1: int = 0

class XErhaltungsaufwand:
    def __init__(self, valuedict:Dict=None ):
        self.master_name:str = ""
        self.master_id:int = 0
        self.mobj_id:str = ""
        self.betrag:float = 0.0
        self.kreditor:str = ""
        self.rgdatum:str = ""
        self.rgtext:str = ""
        self.verteilen_auf_jahre = 1
        self.buchungsdatum:str = ""
        self.buchungsjahr:int = 0
        self.buchungstext:str = ""
        if valuedict:
            setFromDict( self, valuedict )

class XAllgemeineKosten( XErhaltungsaufwand ):
    def __init__( self, valuedict:Dict=None ):
        XErhaltungsaufwand.__init__( self, valuedict )

class XSonstigeKosten( XErhaltungsaufwand ):
    def __init__( self, valuedict:Dict=None ):
        XErhaltungsaufwand.__init__( self, valuedict )

class XSammelAbgabeDetail:
    """
    Für die Whgen in NK und OTW werden die Abgaben in einer Summe erhoben.
    In der Tabelle sonstaus findet sich bei Abbuchung nur ein Eintrag der Art:
        master_id=29 ("*NK_Alle*), betrag=-700, kostenart='sam', buchungstext='PK:00.01365.2'.
    Diesen Eintrag kann man keinem Masterobjekt zuordnen. Deshalb ist dieser Sammelbetrag
    aufgesplittet in Detail-Beträge der Masterobjekte in der Tabelle sammelabgabe_detail.
    Für jedes Objekt muss in dieser Tabelle nachgeschaut werden, ob Einträge vorhanden sind.
    """
    def __init__(self, valuedict:Dict=None ):
        self.master_name:str = ""
        self.master_id = 0
        self.grundsteuer:float = 0.0
        self.abwasser:float = 0.0
        self.strassenreinigung:float = 0.0
        if valuedict:
            setFromDict( self, valuedict )

class XWerbungskosten:
    def __init__( self, master_name:str, jahr:int ):
        self.master_name:str = master_name
        self.jahr:int = jahr
        self.afa:XAfA = None
        self.erhalt_aufwand:int = 0 # die Summe der im VJ komplett anzusetzenden Aufwände
        self.erhalt_aufwand_verteilt:XAufwandVerteilt = None
        self.kostenart_a = 0  # ohne Versicherungen und Grundsteuer und bei NK- und OTW-Wohnungen ohne komm. Abgaben
        self.grundsteuer = 0
        self.strassenreinigung = 0
        self.abwasser = 0
        self.versicherungen = 0
        self.allgemeine_kosten_summe = 0
        self.allgemeine_kosten_gruppiert:List[XAusgabeKurz] = list()
        self.sonstige_kosten = 0

    def getSummeAllgemeineKosten( self ) -> float:
        #print( self.master_name )
        return self.kostenart_a + self.versicherungen + self.grundsteuer + self.abwasser + self.strassenreinigung

    def getSummeWerbungskosten( self ) -> int:
        av = self.erhalt_aufwand_verteilt
        sum = self.afa.afa + self.erhalt_aufwand + \
               av.aufwand_vj + av.aufwand_vj_minus_1 + av.aufwand_vj_minus_2 + \
               av.aufwand_vj_minus_3 + av.aufwand_vj_minus_4 + \
               self.getSummeAllgemeineKosten() + \
               self.sonstige_kosten
        return int( round( sum ) )

class XAnlageV_Daten:
    def __init__( self ):
        self.steuerpflichtiger: XSteuerpflichtiger = None
        self.objektstammdaten: XObjektStammdaten = None
        self.mieteinnahmen:XMieteinnahme = None

class XZeilendefinition:
    def __init__( self, valuedict:Dict=None ):
        self.zeile:int = 0 # Nummer der Zeile auf dem AnlageV-Formular
        self.feld_id:str = "" # z.B. "vorname"
        self.feld_nr:int = 0  # z.B. 3
        self.print_flag:bool = True
        self.printX:int = 0
        self.printY:int = 0
        self.new_page_after:bool = False
        self.rtl:bool = False
        if valuedict:
            setFromDict( self, valuedict )

class XObjektStammdaten:
    def __init__( self, valuedict:Dict=None ):
        self.lfdnr = 0 # Anlage V - "lfd. Nr. der Anlage"
        self.master_id = 0
        self.master_name = ""
        self.plz:str = ""
        self.ort:str = ""
        self.strasse_hnr:str = ""
        self.angeschafft_am = ""
        self.veraeussert_am = ""
        self.gesamt_wfl = 0
        self.einhwert_az = ""
        if valuedict:
            setFromDict( self, valuedict )

class XAnlageV_Zeile:
    """
    Enthält die Daten, die als Zeilen in der Anlage V ausgegeben werden und zusätzlich
    die Daten, die - ebenfalls als Zeilen - in der Preview-Tabelle gezeigt werden.
    """
    def __init__( self, nr:int=0, feld_id:str = None, value:str=None,
                  teilbetrag:float=None, betrag:int=None,
                  bemerkung:str=None, fontFlag:int=0 ):
        self.nr:int = nr  # entspricht der Zeilennummer der Anlage V bzw. ist 0,
                          # wenn diese Zeile nur auf der Preview ausgegeben wird
        self.feld_id = feld_id # entspricht der feld_id in Tabelle anlagev_layout
        self.value:str = value
        self.isCaption:bool = False # um die Überschriften in der Preview zu kennzeichnen
        self.teilbetrag = teilbetrag # nur für die Preview vorgesehen - wird nicht auf die Anlage V gedruckt
        self.betrag = betrag
        self.bemerkung = bemerkung
        self.fontFlag = fontFlag  # 0:normal, 1:bold, 2:big bold
        self.previewFlag:bool = True # diese Zeile in der Preview-Tabelle anzeigen
        #self.printFlag:bool = True # diese Zeile drucken
        self.printX = 0 # when printing: x-position of value in mm
        self.printY = 0 # when printing: y-position of value in mm
        self.new_page_after:bool = False
        self.printFontsize = 5
        self.rtl:bool = False # True: Druck rechtsbündig

    def getDisplayItemCount( self ) -> int:
        return 6 # nr, feld_id, value, teilbetrag, betrag, bemerkung

    def getHeaders( self ) -> List:
        return ["Zeile", "Feld", "Text", "Teilbetrag", "Betrag", "Bemerkung"]

    def getValue( self, column:int ) -> Any:
        """
        Wird vom TableModel aufgerufen und liefert den zr column passenden Wert.
        :param column:
        :return:
        """
        if column == 0: return self.nr
        if column == 1: return self.feld_id
        if column == 2: return self.value
        if column == 3: return self.teilbetrag
        if column == 4: return self.betrag
        if column == 5: return self.bemerkung

    def getBetragColumn( self ) -> int:
        return 4
