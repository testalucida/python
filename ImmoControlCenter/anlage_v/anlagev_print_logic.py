import numbers
from typing import List, Dict, Any

from PySide2.QtWidgets import QApplication

from anlage_v.anlagev_base_logic import AnlageV_Base_Logic, masterobjekte
from anlage_v.anlagev_interfaces import XAnlageV_Zeile, XMieteinnahme
from anlage_v.anlagev_printer import AnlageV_Printer


class AnlageV_Print_Logic( AnlageV_Base_Logic):
    def __init__(self):
        AnlageV_Base_Logic.__init__( self )

    def printAnlagenV( self, master_names:List[str], jahr:int ):
        for master_name in master_names:
            zeilenlist = self._getAnlageV_Zeilen( master_name, jahr )
            avprinter = AnlageV_Printer( zeilenlist )
            avprinter.print()
        self.terminate()

    def testPrint( self, feld_id:str, value:Any ) -> None:
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( feld_id, value )
        l = list()
        l.append( z )
        avprinter = AnlageV_Printer( l )
        avprinter.print()
        self.terminate()

    def _getAnlageV_Zeilen( self, master_name: str, jahr: int ) -> List[XAnlageV_Zeile]:
        """
        liefert alle Zeilen für den Druck der AnlageV des Objekts master_name (N_Stadtpark etc.)
        :param master_name:
        :return:
        """
        l: List[XAnlageV_Zeile] = list()
        self._provideFirstSteuerpflichtigen( l )
        self._provideObjekt( master_name, l )
        self._provideMieteinnahmenUndUmlagen( master_name, jahr, l )
        return l

    def _provideFirstSteuerpflichtigen( self, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        """
        liefert den ersten Eintrag der Tabelle steuerpflichtiger.
        Das bin ich ;-)  Ich mach das nur, um meinen Namen u. meine Steuernummer nicht im Programm verdrahten zu müssen.
        Geliefert wird ein Dictionary mit den Keys name, vorname, steuernummer
        :return:
        """
        ld: List[Dict] = self._db.getSteuerpflichtige()
        d = ld[0]  # das bin ich
        x = self._createAnlageV_Zeile( "name", d["name"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "zur_est", "X" )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "vorname", d["vorname"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "steuernummer", d["steuernummer"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )

    def _provideObjekt( self, master_name: str, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        """
        fügt der Liste der AnlageV-Zeilen die 6 objektspezifischen Felder hinzu
        :param master_name: Identifikation des Mietobjekts
        :param anlagev_zeilen:
        :return:
        """
        o = self.getObjekt( master_name )
        x = self._createAnlageV_Zeile( "lfdnr", o.lfdnr )
        x.previewFlag = False
        anlagev_zeilen.append( x )

        x = self._createAnlageV_Zeile( "obj_str_hnr", o.strasse_hnr )
        anlagev_zeilen.append( x )

        x = self._createAnlageV_Zeile( "angeschafft_am", o.angeschafft_am )
        x.previewFlag = False
        anlagev_zeilen.append( x )

        x = self._createAnlageV_Zeile( "obj_plz", o.plz )
        anlagev_zeilen.append( x )

        x = self._createAnlageV_Zeile( "obj_ort", o.ort )
        anlagev_zeilen.append( x )

        x = self._createAnlageV_Zeile( "veraeussert_am", o.veraeussert_am )
        x.previewFlag = False
        anlagev_zeilen.append( x )

        # Gesamtwohnfläche
        x = self._createAnlageV_Zeile( "gesamt_wfl", o.gesamt_wfl )
        anlagev_zeilen.append( x )

    def _provideMieteinnahmenUndUmlagen( self, master_name: str, jahr: int,
                                         anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        x: XMieteinnahme = self.getMieteinnahmenUndNebenkosten( master_name, jahr )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "mieteinnahmen_netto", x.nettoMiete )
        anlagev_zeilen.append( z )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "umlagen", x.nkv + x.nka )
        anlagev_zeilen.append( z )

    def _createAnlageV_Zeile( self, feld_id: str, val: Any ) -> XAnlageV_Zeile:
        defi = self._getZeilenDef( feld_id )
        x = XAnlageV_Zeile()
        x.nr = defi.zeile
        x.feld_id = feld_id
        x.printX = defi.printX
        x.printY = defi.printY
        if isinstance( val, numbers.Number ):
            if val < 100:
                x.printX += 5
            if val > 999:
                x.printX -= 5
            if val > 9999:
                x.printX -= 5
            val = str( val )
        x.value = val
        x.new_page_after = True if defi.new_page_after == 1 else False
        return x

##################################################################################
########## !!!!!!DRUCKER AUF EINZELBLATT STELLEN!!!!!!!!!!!!!! ###################
def testPrint():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    busi.printAnlagenV( ["SB_Kaiser",], 2021 )

def testPrintOneLineOnly():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    busi.testPrint( "zurechng_stpfl", 12985 )

if __name__ == "__main__":
    testPrint()
    #testPrintOneLineOnly()