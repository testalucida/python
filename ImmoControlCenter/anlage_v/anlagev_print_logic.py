import numbers
from typing import List, Dict, Any

from PySide2.QtPrintSupport import QPrintDialog
from PySide2.QtWidgets import QApplication, QDialog

from anlage_v.anlagev_base_logic import AnlageV_Base_Logic, masterobjekte
from anlage_v.anlagev_interfaces import XAnlageV_Zeile, XMieteinnahme, XWerbungskosten, XAfA, XAufwandVerteilt
from anlage_v.anlagev_printer import AnlageV_Printer


class AnlageV_Print_Logic( AnlageV_Base_Logic):
    def __init__(self):
        AnlageV_Base_Logic.__init__( self )
        self._page = 1

    def printAnlagenVAll( self, jahr, nurKopfdaten:bool=False ):
        master_names = self.getObjektNamen()
        self.printAnlagenV( master_names, nurKopfdaten )

    def printAnlagenV( self, master_names:List[str], jahr:int, nurKopfdaten:bool=False ):
        avprinter = AnlageV_Printer()
        if avprinter.showPrintDialog():
            for master_name in master_names:
                zeilenlist = self._getAnlageV_Zeilen( master_name, jahr, nurKopfdaten )
                avprinter.print( zeilenlist )
            avprinter.end()
        self.terminate()

    def testPrint( self, feld_id:str, value:Any ) -> None:
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( feld_id, value )
        l = list()
        l.append( z )
        avprinter = AnlageV_Printer()
        if avprinter.showPrintDialog():
            avprinter.print( l )
            avprinter.end()
        self.terminate()

    def testPrintSomeLines( self, fields:List[Dict] ) -> None:
        """
        fields: List of dictionaries like so:
        {
            id: "summe_einnahmen",
            value: 1234
        }
        :param fields:
        :return:
        """
        l = list()
        for f in fields:
            z: XAnlageV_Zeile = self._createAnlageV_Zeile( f["id"], f["value"] )
            l.append( z )
        avprinter = AnlageV_Printer()
        if avprinter.showPrintDialog():
            avprinter.print( l )
            avprinter.end()
        self.terminate()

    def _getAnlageV_Zeilen( self, master_name: str, jahr: int, nurKopfdaten:bool=False ) -> List[XAnlageV_Zeile]:
        """
        liefert alle Zeilen für den Druck der AnlageV des Objekts master_name (N_Stadtpark etc.)
        :param master_name:
        :return:
        """
        l: List[XAnlageV_Zeile] = list()
        ################### Seite 1
        # Kopfdaten
        dic = self._db.getSteuerpflichtiger( master_name )
        self._provideSteuerpflichtigen( dic, l )
        self._provideObjekt( master_name, l )
        if nurKopfdaten: return l
        # Einnahmen, Werbungskosten, Überschuss
        xme: XMieteinnahme = self.getMieteinnahmenUndNebenkosten( master_name, jahr )
        self._provideMieteinnahmenUndUmlagen( xme, l )
        self._provideSummeEinnahmen( xme, l )
        xwk:XWerbungskosten = self.getWerbungskosten( master_name, jahr )
        summeWk = xwk.getSummeWerbungskosten()
        self._provideSummeWerbungskosten( summeWk, l )
        ueberschuss = self._provideUeberschuss( xme, xwk, l )
        self._provideZurechnungBetrag( ueberschuss, l )
        ################### Seite 2
        self._provideAfA( xwk.afa, l )
        self._provideAufwandVollAbziehbar( xwk.erhalt_aufwand, l )
        self._provideAufwandVerteilt( xwk.erhalt_aufwand_verteilt, l )
        self._provideAllgemeineKosten( xwk.getSummeAllgemeineKosten(), l )
        self._provideSonstigeKosten( xwk.sonstige_kosten, l )
        self._provideSummeWerbungskostenUebertrag( summeWk, l )
        return l

    def _provideSteuerpflichtigen( self, stpfldic:Dict, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        """
        Erzeugt AnlageV-Zeilen für den Steuerpflichtigen
        :param stpfldic: Dict mit den keys name, vorname, steuernummer
        :param anlagev_zeilen: Liste der Zeilen
        :return:
        """
        x = self._createAnlageV_Zeile( "name", stpfldic["name"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "zur_est", "X" )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "vorname", stpfldic["vorname"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "steuernummer", stpfldic["steuernummer"] )
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

    def _provideMieteinnahmenUndUmlagen( self, xme:XMieteinnahme,
                                         anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        # x: XMieteinnahme = self.getMieteinnahmenUndNebenkosten( master_name, jahr )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "mieteinnahmen_netto", xme.nettoMiete )
        anlagev_zeilen.append( z )
        umlagen = self.getSaldoNebenkostenAusXMieteinnahme( xme )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "umlagen", umlagen )
        anlagev_zeilen.append( z )

    def _provideSummeEinnahmen( self, xme:XMieteinnahme, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        summeEin:int = self.getSummeEinnahmenAusXMieteinnahme( xme )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "summe_einnahmen", summeEin )
        anlagev_zeilen.append( z )

    def _provideSummeWerbungskosten( self, summeWk:int, anlagev_zeilen: List[XAnlageV_Zeile] ):
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "summe_werbungskosten_uebertrag", abs( summeWk ) )
        anlagev_zeilen.append( z )

    def _provideUeberschuss( self, xme:XMieteinnahme, xwk:XWerbungskosten, anlagev_zeilen: List[XAnlageV_Zeile] ) -> int:
        ueberschuss:int = self.getUeberschuss( xme, xwk )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "ueberschuss", ueberschuss )
        anlagev_zeilen.append( z )
        return ueberschuss

    def _provideZurechnungBetrag( self, betrag:int, anlagev_zeilen: List[XAnlageV_Zeile] ):
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "zurechng_stpfl", betrag )
        anlagev_zeilen.append( z )

    def _provideAfA( self, xafa:XAfA, anlagev_zeilen: List[XAnlageV_Zeile] ):
        if xafa.afa_linear:
            z: XAnlageV_Zeile = self._createAnlageV_Zeile( "afa_linear", "X" )
            anlagev_zeilen.append( z )
        if xafa.afa_prozent > 0:
            z: XAnlageV_Zeile = self._createAnlageV_Zeile( "afa_prozent", xafa.afa_prozent )
            anlagev_zeilen.append( z )
        if xafa.afa_wie_vorjahr:
            z: XAnlageV_Zeile = self._createAnlageV_Zeile( "afa_wie_vorjahr", "X" )
            anlagev_zeilen.append( z )
        if xafa.afa < 0:
            z: XAnlageV_Zeile = self._createAnlageV_Zeile( "afa_betrag", abs( xafa.afa ) )
            anlagev_zeilen.append( z )

    def _provideAufwandVollAbziehbar( self, aufwand:int, anlagev_zeilen: List[XAnlageV_Zeile] ):
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "kosten_voll_abziehbar", abs( aufwand ) )
        anlagev_zeilen.append( z )

    def _provideAufwandVerteilt( self, aufwand:XAufwandVerteilt, anlagev_zeilen: List[XAnlageV_Zeile] ):
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "kosten_zu_verteilen", abs( aufwand.gesamt_aufwand_vj ) )
        anlagev_zeilen.append( z )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "davon_im_vj", abs( aufwand.aufwand_vj ) )
        anlagev_zeilen.append( z )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "anteil_aus_vj_minus_4", abs( aufwand.aufwand_vj_minus_4 ) )
        anlagev_zeilen.append( z )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "anteil_aus_vj_minus_3", abs( aufwand.aufwand_vj_minus_3 ) )
        anlagev_zeilen.append( z )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "anteil_aus_vj_minus_2", abs( aufwand.aufwand_vj_minus_2 ) )
        anlagev_zeilen.append( z )
        z: XAnlageV_Zeile = self._createAnlageV_Zeile( "anteil_aus_vj_minus_1", abs( aufwand.aufwand_vj_minus_1 ) )
        anlagev_zeilen.append( z )

    def _provideAllgemeineKosten( self, allgemeinkosten: int, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        """
        :param allgemeinkosten: Summe aus Kostenart 'a', Versicherungen, Grundsteuer, Abwasser, Straßenreinigung.
        :param anlagev_zeilen:
        :return:
        """
        x = self._createAnlageV_Zeile( "hauskosten_allg", abs( allgemeinkosten ) )
        x.previewFlag = False
        anlagev_zeilen.append( x )

    def _provideSonstigeKosten( self, sonstigeKosten: int, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        x = self._createAnlageV_Zeile( "sonstige_kosten", abs( sonstigeKosten ) )
        x.previewFlag = False
        anlagev_zeilen.append( x )

    def _provideSummeWerbungskostenUebertrag( self, summeWk: int, anlagev_zeilen: List[XAnlageV_Zeile] ) -> None:
        x = self._createAnlageV_Zeile( "summe_werbungskosten", abs( summeWk ) )
        x.previewFlag = False
        anlagev_zeilen.append( x )

    def _createAnlageV_Zeile( self, feld_id: str, val: Any, page:int=1 ) -> XAnlageV_Zeile:
        defi = self._getZeilenDef( feld_id )
        x = XAnlageV_Zeile()
        x.nr = defi.zeile
        x.feld_id = feld_id
        x.rtl = defi.rtl

        if defi.rtl: # print right to left
            # maxX = 194 if self._page == 1 else 186  # letzte Ziffer in letzter Spalte
            # w = 30 # width of printing rectangle
            # x.printX = maxX - w # left top x value
            x.printX = 166 if self._page == 1 else 156
            x.printY = defi.printY - 3 # top y value
        else:
            x.printX = defi.printX
            x.printY = defi.printY

        # if isinstance( val, numbers.Number ):
        #     if val < 100:
        #         x.printX += 3
        #     if val > 999:
        #         x.printX -= 3
        #     if val > 9999:
        #         x.printX -= 3
        #     val = str( val )

        if isinstance( val, numbers.Number ):
            val = str( int( round( val ) ) )
        x.value = val
        x.new_page_after = defi.new_page_after
        if defi.new_page_after:
            self._page = 2
        return x

##################################################################################
########## !!!!!!DRUCKER AUF EINZELBLATT STELLEN!!!!!!!!!!!!!! ###################
def testPrint():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    busi.printAnlagenVAll( 2021, nurKopfdaten=True )
    busi.printAnlagenV( ["SB_Kaiser",], 2021, nurKopfdaten=True )

def testPrintOneLineOnly():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    busi._page = 2
    busi.testPrint( "kosten_voll_abziehbar", 12985 )

def testPrintAllgemeineUndSonstigeKosten():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    busi._page = 2
    l = list()
    d = { "id": "hauskosten_allg",
          "value": 3210 }
    l.append( d )
    d = { "id": "sonstige_kosten",
          "value": 543 }
    l.append( d )
    d = { "id": "summe_werbungskosten",
          "value": 6543 }
    l.append( d )

    busi.testPrintSomeLines( l )

def testPrintKosten():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    busi._page = 2
    l = list()
    # d = { "id": "kosten_voll_abziehbar",
    #       "value": 14000 }
    # l.append( d )
    # d = { "id": "kosten_zu_verteilen",
    #       "value": 20000 }
    # l.append( d )
    d = { "id": "davon_im_vj",
          "value": 4000 }
    l.append( d )
    d = { "id": "anteil_aus_vj_minus_4",
          "value": 4444 }
    l.append( d )
    d = { "id": "anteil_aus_vj_minus_3",
          "value": 3333 }
    l.append( d )
    d = { "id": "anteil_aus_vj_minus_2",
          "value": 2222 }
    l.append( d )
    d = { "id": "anteil_aus_vj_minus_1",
          "value": 1111 }
    l.append( d )
    busi.testPrintSomeLines( l )

def testPrintAfA():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    l = list()
    d = { "id": "afa_linear",
          "value": "X" }
    l.append( d )
    d = { "id": "afa_wie_vorjahr",
          "value": "X" }
    l.append( d )
    d = { "id": "afa_betrag",
          "value": 4321 }
    l.append( d )
    busi.testPrintSomeLines( l )

def testPrintSomeLines():
    app = QApplication()
    busi = AnlageV_Print_Logic()
    l = list()
    d = {"id": "summe_einnahmen",
         "value": 13000}
    l.append( d )
    d = {"id": "summe_werbungskosten_uebertrag",
         "value": 4132}
    l.append( d )
    d = { "id": "ueberschuss",
          "value": 132 }
    l.append( d )
    busi.testPrintSomeLines( l )

if __name__ == "__main__":
    #testPrint()
    #testPrintOneLineOnly()
    #testPrintSomeLines()
    #testPrintAfA()
    #testPrintKosten()
    testPrintAllgemeineUndSonstigeKosten()