from typing import Any, List, Dict

from interfaces import XBase


class XSteuerpflichtiger:
    def __init__( self ):
        self.name = "Kendel"
        self.vorname = "Martin"
        self.steuernummer = ""

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
    def __init__( self, nr:int=0, text:str=None,
                  teilbetrag:float=None, betrag:int=None,
                  bemerkung:str=None, fontFlag:int=0 ):
        self.nr:int = nr
        self.text:str = text
        self.teilbetrag = teilbetrag
        self.betrag = betrag
        self.bemerkung = bemerkung
        self.fontFlag = fontFlag  # 0:normal, 1:bold, 2:big bold
        self.printX = 0 # when printing: x-position of value in mm
        self.printY = 0 # when printing: y-position of value in mm
        self.printFontsize = 6

    def getDisplayItemCount( self ) -> int:
        return 5 # nr, text, teilbetrag, betrag, bemerkung

    def getHeaders( self ) -> List:
        return ["Zeile", "Text", "Teilbetrag", "Betrag", "Bemerkung"]

    def getValue( self, column:int ) -> Any:
        if column == 0: return self.nr
        if column == 1: return self.text
        if column == 2: return self.teilbetrag
        if column == 3: return self.betrag
        if column == 4: return self.bemerkung

    def getBetragColumn( self ) -> int:
        return 3
