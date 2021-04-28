from typing import List, Dict, Any

from PySide2.QtWidgets import QApplication

from anlage_v.anlagev_dataacess import AnlageV_DataAccess
from anlage_v.anlagev_interfaces import XObjektStammdaten, XAnlageV_Zeile, XZeilendefinition
from anlage_v.anlagev_printer import AnlageV_Printer
import numbers

from anlage_v.anlagev_tablemodel import AnlageVTableModel
from anlage_v.anlagev_view import AnlageVView
from constants import Zahlart
from datehelper import getNumberOfMonths
from interfaces import XSollMiete


class AnlageV_Logic:
    __instance = None

    def __init__(self):
        if AnlageV_Logic.__instance != None:
            raise Exception( "You can't instantiate AnlageV_Logic more than once." )
        else:
            AnlageV_Logic.__instance = self
        self._db: AnlageV_DataAccess
        self._steuerpflichtiger:Dict = dict() #keys: name, vorname, steuerpflichtiger
        self._objektStammdatenList:List[XObjektStammdaten] = list()
        self._anlageV_zeilendefinitionen:List[XZeilendefinition] = list()

    @staticmethod
    def inst() -> __instance:
        if AnlageV_Logic.__instance == None:
            AnlageV_Logic()
            AnlageV_Logic.inst()._prepare()
        return AnlageV_Logic.__instance

    def _prepare(self):
        dbname = "../immo.db"
        #dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"
        self._db = AnlageV_DataAccess( dbname )
        self._db.open()
        self._steuerpflichtiger = self._db.getSteuerpflichtige()[0]
        self._objektStammdatenList:List[XObjektStammdaten] = self._db.getObjektStammdaten()
        self._anlageV_zeilendefinitionen:List[XZeilendefinition] = self._db.getAnlageV_Zeilendefinitionen()

    def terminate(self):
        self._db.close()

    def _getZeilenDef( self, feld_id:str ) -> XZeilendefinition:
        """
        liefert zur feld_id (Bsp: "vorname" die Nummer der entsprechenden Zeile in der Anlage V
        :param feld_id:
        :return:
        """
        for defi in self._anlageV_zeilendefinitionen:
            if defi.feld_id == feld_id:
                return defi
        raise Exception( "AnlageV_Logic._getZeilenDef(): kann Feld_Id '%s' nicht finden." % (feld_id) )

    def _createAnlageV_Zeile( self, feld_id:str, val:Any ) -> XAnlageV_Zeile:
        defi = self._getZeilenDef( feld_id )
        x = XAnlageV_Zeile()
        x.nr = defi.zeile
        x.feld_id = feld_id
        if isinstance(val, numbers.Number):
            val = str( val )
        x.value = val
        x.printX = defi.printX
        x.printY = defi.printY
        x.new_page_after = True if defi.new_page_after == 1 else False
        return x

    def _provideFirstSteuerpflichtigen( self, anlagev_zeilen:List[XAnlageV_Zeile] ) -> None:
        """
        liefert den ersten Eintrag der Tabelle steuerpflichtiger.
        Das bin ich ;-)  Ich mach das nur, um meinen Namen u. meine Steuernummer nicht im Programm verdrahten zu müssen.
        Geliefert wird ein Dictionary mit den Keys name, vorname, steuernummer
        :return:
        """
        ld:List[Dict] = self._db.getSteuerpflichtige()
        d = ld[0] # das bin ich
        x = self._createAnlageV_Zeile( "name", d["name"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "vorname", d["vorname"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )
        x = self._createAnlageV_Zeile( "steuernummer", d["steuernummer"] )
        x.previewFlag = False
        anlagev_zeilen.append( x )

    def _getObjekt( self, master_name:str ) -> XObjektStammdaten:
        for o in self._objektStammdatenList:
            if o.master_name == master_name: return o
        raise Exception( "AnlageV_Logic._getObjekt(): "
                         "Objekt '%s' nicht in der Objektliste gefunden." % (master_name) )

    def _provideObjekt( self, master_name:str, anlagev_zeilen:List[XAnlageV_Zeile] ) -> None:
        """
        fügt der Liste der AnlageV-Zeilen die 6 objektspezifischen Felder hinzu
        :param master_name: Identifikation des Mietobjekts
        :param anlagev_zeilen:
        :return:
        """
        o = self._getObjekt( master_name )
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

    def _provideMieteinnahmenUndUmlagen( self, master_name:str, jahr:int, anlagev_zeilen:List[XAnlageV_Zeile] ) -> None:
        """
        Hier werden die Zeilen für die Netto-Miete und die Nebenkosten versorgt.
        Die Nebenkosten (NK) teilen sich auf in NK-Vorauszahlungen (NKV) und NK-Abrechnungen (NKA).
        Zunächst werden die Brutto-Mieteinnahmen für ein Master-Objekt wie folgt ermittelt:
            a) Summe der Mieteingänge aus der Tabelle zahlungen
            b) offene Forderungen des Mieters an mich aus der NKA. Es gibt nämlich Spezialisten, die mir
               kein Bankkonto für die NKA-Rückzahlung mitteilen, sondern einfach die nächste Miete kürzen.
               Wenn man also nur die Mieteinnahmen aus der Tabelle zahlungen berücksichtigen würde,
               ergäbe sich eine offene Forderung von mir an den betreffenden Mieter.
        Die Summe aus a + b ist Jahres-Bruttosumme.
        NB: der andere Fall, eine offene Forderung an den Mieter (NK-Nachzahlung), muss nicht betrachtet
        werden. Das ist einfach eine fehlende Einnahme im Jahr jahr, die nach Begleichung im Folgejahr
        als Einnahme verbucht wird.

        Dann wird aus Tabelle sollmiete das Soll-Jahresnetto ermittelt.
        Ist das Soll <= dem Ist-Brutto, wird es in die AnlageV (Feld Mieteinnahmen für Wohnungen, Z. 9)
        eingetragen.
        Ist das Ist-Brutto kleiner als das Netto-Soll (ist noch nie vorgekommen), wird das Ist-Brutto in
        die Anlage V ins Feld "Mieteinnahmen ohne Umlagen", Z.9,  eingetragen. In diesem Fall werden keine NKV
        in Feld Umlagen, Z. 13, eingetragen.
        Im Normalfall (Ist-Brutto > Soll-Netto) wird das Soll-Netto ins Feld "Mieteinnahmen ohne Umlagen"
        eingetragen und die Differenz Ist-Brutto - Soll-Netto abgezogen (ergibt die NKV)
        ins Feld "Umlagen", Z. 13.

        Aus der Tabelle nk_abrechnung werden nun noch gebuchte Beträge (Rück- oder Nachzahlungen) von Mietern
        der Mietobjekte des Master-OBjekts mit den NKV saldiert; der sich ergebende Wert wird in Feld Umlagen
        eingetragen.
        :param master_name:
        :param jahr:
        :param anlagev_zeilen:
        :return:
        """
        bruttoME = self._db.getZahlungssumme( master_name, jahr, Zahlart.BRUTTOMIETE )
        offErstattg = self._db.getOffeneNKErstattungen( master_name, jahr-1 )
        bruttoME += offErstattg
        nettoSoll = self._getJahresNettoSoll( master_name, jahr )
        nka = self._db.getNKA( master_name, jahr )
        if bruttoME < nettoSoll: # der unwahrscheinliche Fall
            self._createAnlageV_Zeile( "mieteinnahmen_netto", bruttoME )
            self._createAnlageV_Zeile( "umlagen", nka )
        else:
            self._createAnlageV_Zeile( "mieteinnahmen_netto", nettoSoll )
            nkv = bruttoME - nettoSoll # das sind die NKV
            self._createAnlageV_Zeile( "umlagen", nkv + nka )

    def _getJahresNettoSoll( self, master_name:str, jahr:int ):
        sollmieten: List[XSollMiete] = self._getSollmieten( master_name, jahr )
        nettoSoll = 0
        for sollmiete in sollmieten:
            nMonate = getNumberOfMonths( sollmiete.von, sollmiete.bis, jahr )
            nettoSoll += nMonate * sollmiete.netto
        return nettoSoll

    def _getSollmieten( self, master_name, jahr:int ) -> List[XSollMiete]:
        return self._db.getSollmietenFuerMasterobjekt( master_name, jahr )

    def getObjektStammdatenList( self ) -> List[XObjektStammdaten]:
        return self._objektStammdatenList

    def getObjektNamen( self ) -> List[str]:
        """
        Liefert alle master_name aus der Tabelle masterobjekt,
        sortiert nach Name aufsteigend OHNE Namen wie "**alle**"
        :return:
        """
        return self._db.getObjektNamen()

    def getAnlageV_Zeilen( self, master_name:str, jahr:int ) -> List[XAnlageV_Zeile]:
        """
        liefert alle Zeilen für die AnlageV des Objekts master_name (N_Stadtpark etc.)
        :param master_name:
        :return:
        """
        l:List[XAnlageV_Zeile] = list()
        self._provideFirstSteuerpflichtigen( l )
        self._provideObjekt( master_name, l )
        self._provideMieteinnahmenUndUmlagen( master_name, jahr, l )
        return l

# masterobjekte = [ "BUEB_Saargemuend", "HOM_Remigius",
#                   "ILL_Eich",
#                   "NK_Kleist", "NK_KuchenbergS", "NK_KuchenbergW", "NK_ThomasMann", "NK_Volkerstal",
#                   "NK_Ww224", "NK_Zweibrueck", "OTW_Linx", "OTW_Schwalbe", "RI_Lampennester",
#                   "SB_Charlotte", "SB_Gruelings", "SB_Hohenzoll", "SB_Kaiser" ]
masterobjekte = [ "ILL_Eich", "SB_Hohenzoll", "SB_Kaiser" ]

def testPreview():
    app = QApplication()
    busi = AnlageV_Logic.inst()
    v = AnlageVView()
    zeilenlist = busi.getAnlageV_Zeilen( "BUEB_Saargemuend", 2021 )
    m = AnlageVTableModel( zeilenlist )
    v.setAnlageVTableModel( m )
    v.show()
    app.exec_()

def test():
    busi = AnlageV_Logic.inst()
    sm_list = busi._getSollmieten( "N_Lamm", 2020 )
    zeilenlist = busi.getAnlageV_Zeilen( "BUEB_Saargemuend" )

    # d = busi.getFirstSteuerpflichtigen()
    # print( d )
    # o = busi.getObjektStammdaten()
    # print( o )
    busi.terminate()

def printAll():
    ###### ACHTUNG: Drucker auf EINSEITIG stellen!!!!!!!!!!!!!
    app = QApplication()
    busi = AnlageV_Logic.inst()
    for masterobjekt in masterobjekte:
        zeilenlist = busi.getAnlageV_Zeilen( masterobjekt, 2020 )
        avprinter = AnlageV_Printer( zeilenlist )
        avprinter.print()

def testPrint():
    busi = AnlageV_Logic.inst()
    zeilenlist = busi.getAnlageV_Zeilen( "BUEB_Saargemuend" )
    busi.terminate()

    app = QApplication()
    avprinter = AnlageV_Printer( zeilenlist )
    avprinter.print()


if __name__ == "__main__":
    #test()
    #testPrint()
    #printAll()
    testPreview()