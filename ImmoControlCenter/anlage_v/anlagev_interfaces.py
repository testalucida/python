from typing import Any, List, Dict

from interfaces import XBase


class XSteuerpflichtiger:
    def __init__( self ):
        self.name = "Kendel"
        self.vorname = "Martin"
        self.steuernummer = ""

class XZeilendefinition( XBase ):
    def __init__( self, valuedict:Dict=None ):
        self.zeile:int = 0 # Nummer der Zeile auf dem AnlageV-Formular
        self.feld_id:str = "" # z.B. "vorname"
        self.feld_nr:int = 0  # z.B. 3
        self.print_flag:bool = True
        self.printX:int = 0
        self.printY:int = 0
        self.new_page_after:int = 0
        if valuedict: self.setFromDict( valuedict )

class XObjektStammdaten( XBase ):
    def __init__( self, valuedict:Dict=None ):
        self.master_id = 0
        self.master_name = ""
        self.plz:str = ""
        self.ort:str = ""
        self.strasse_hnr:str = ""
        self.angeschafft_am = ""
        self.veraeussert_am = ""
        self.gesamt_wfl = 0
        self.einhwert_az = ""
        if valuedict: self.setFromDict( valuedict )

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
        self.printFlag:bool = True # diese Zeile drucken
        self.printX = 0 # when printing: x-position of value in mm
        self.printY = 0 # when printing: y-position of value in mm
        self.new_page_after:bool = False
        self.printFontsize = 5

    def getDisplayItemCount( self ) -> int:
        return 5 # nr, text, teilbetrag, betrag, bemerkung

    def getHeaders( self ) -> List:
        return ["Zeile", "Text", "Teilbetrag", "Betrag", "Bemerkung"]

    def getValue( self, column:int ) -> Any:
        """
        Wird vom TableModel aufgerufen und liefert den zr column passenden Wert.
        :param column:
        :return:
        """
        if column == 0: return self.nr
        if column == 1: return self.text
        if column == 2: return self.teilbetrag
        if column == 3: return self.betrag
        if column == 4: return self.bemerkung

    def getBetragColumn( self ) -> int:
        return 3
