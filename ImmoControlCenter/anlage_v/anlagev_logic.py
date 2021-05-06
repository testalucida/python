from typing import List, Dict, Any

from PySide2.QtWidgets import QApplication

from anlage_v.anlagev_dataacess import AnlageV_DataAccess
from anlage_v.anlagev_interfaces import XObjektStammdaten, XAnlageV_Zeile, XZeilendefinition, XMieteinnahme, \
    XWerbungskosten, XAfA, XErhaltungsaufwand, XAufwandVerteilt
from anlage_v.anlagev_preview import AnlageV_Preview
from anlage_v.anlagev_printer import AnlageV_Printer
import numbers

from anlage_v.anlagev_tablemodel import AnlageVTableModel, PreviewRow
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
        x = self._createAnlageV_Zeile( "zur_est", "X" )
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
        x:XMieteinnahme = self.getMieteinnahmenUndNebenkosten( master_name, jahr )
        z:XAnlageV_Zeile = self._createAnlageV_Zeile( "mieteinnahmen_netto", x.nettoMiete )
        anlagev_zeilen.append( z )
        z:XAnlageV_Zeile = self._createAnlageV_Zeile( "umlagen", x.nkv + x.nka )
        anlagev_zeilen.append( z )

        # bruttoME = self._db.getZahlungssumme( master_name, jahr, Zahlart.BRUTTOMIETE )
        # offErstattg = self._db.getOffeneNKErstattungen( master_name, jahr-1 )
        # bruttoME += offErstattg
        # nettoSoll = self._getJahresNettoSoll( master_name, jahr )
        # nka = self._db.getNKA( master_name, jahr )
        # if bruttoME < nettoSoll: # der unwahrscheinliche Fall
        #     self._createAnlageV_Zeile( "mieteinnahmen_netto", bruttoME )
        #     self._createAnlageV_Zeile( "umlagen", nka )
        # else:
        #     self._createAnlageV_Zeile( "mieteinnahmen_netto", nettoSoll )
        #     nkv = bruttoME - nettoSoll # das sind die NKV
        #     self._createAnlageV_Zeile( "umlagen", nkv + nka )

    def getMieteinnahmenUndNebenkosten( self, master_name:str, jahr:int ) -> XMieteinnahme:
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
        :return:
        """
        x = XMieteinnahme( master_name )
        x.bruttoMiete = self._db.getZahlungssumme( master_name, jahr, Zahlart.BRUTTOMIETE )
        x.offnNkErstattg = self._db.getOffeneNKErstattungen( master_name, jahr-1 )
        x.nettoSoll = self._getJahresNettoSoll( master_name, jahr )
        x.nka = self._db.getNKA( master_name, jahr-1 )
        if ( x.bruttoMiete + x.offnNkErstattg ) < x.nettoSoll: # der unwahrscheinliche Fall
            x.nettoMiete = x.bruttoMiete
            x.bemerkung = "Brutto: %d + Offene NK-Erstattung: %d ist in Summe niedriger als die Soll-Nettomiete %d" % \
                          ( x.bruttoMiete, x.offnNkErstattg, x.nettoSoll )
        else: # Normalfall
            x.nettoMiete = x.nettoSoll
            x.nkv = x.bruttoMiete - x.nettoMiete
        return x

    def getWerbungskosten( self, master_name:str, jahr:int ) -> XWerbungskosten:
        x:XWerbungskosten = XWerbungskosten( master_name, jahr )
        x.afa = self._db.getAfA( master_name )
        x.erhalt_aufwand = self._db.getNichtVerteiltenErhaltungsaufwandSumme( master_name, jahr )
        x.erhalt_aufwand_verteilt = self._getVerteiltenErhaltungsaufwand( master_name, jahr )
        x.allgemeine_kosten = self._db.getAllgemeineKostenSumme( master_name, jahr )
        x.sonstige_kosten = self._db.getSonstigeKostenSumme( master_name, jahr )
        return x

    def _getVerteiltenErhaltungsaufwand( self, master_name:str, jahr:int ) -> XAufwandVerteilt:
        """
        Ermittelt eine Liste mit allen zu verteilenden Aufwänden.
        Diese einzelnen Aufwände müssen in ein XAufwandVerteilt-OBjekt verdichtet werden.
        :return: XAufwandVerteilt
        """
        awlist:List[XErhaltungsaufwand] = self._db.getVerteilteErhaltungsaufwendungen( master_name, jahr )
        x = XAufwandVerteilt( master_name )
        if len( awlist ) > 0:
            for aw in awlist:
                awpart = int( round( aw.betrag / aw.verteilen_auf_jahre ) ) # awpart ist der Teilbetrag der Rechnung,
                                                                            # der im VJ jahr angesetzt werden soll
                if aw.buchungsjahr + 4 == jahr:
                    x.aufwand_vj_minus_4 += awpart
                elif aw.buchungsjahr + 3 == jahr:
                    x.aufwand_vj_minus_3 += awpart
                elif aw.buchungsjahr + 2 == jahr:
                    x.aufwand_vj_minus_2 += awpart
                elif aw.buchungsjahr + 1 == jahr:
                    x.aufwand_vj_minus_1 += awpart
                elif aw.buchungsjahr == jahr:  # neue Großrechnung
                    x.gesamt_aufwand_vj += int( round( aw.betrag ) )
                    x.aufwand_vj += awpart
        return x

    def createAnlageVTableModel( self, master_name:str, jahr:int ) -> AnlageVTableModel:
        """
        TableModel für die AnlageV-Preview in einer QTableView
        :param master_name:
        :param jahr:
        :return:
        """
        tm_rows:List[PreviewRow] = list()
        x = self._getObjekt( master_name )
        self._createPreviewRowsFromObjektdaten( master_name, x.gesamt_wfl, tm_rows )
        self._createPreviewRowSeparator( "EINNAHMEN und NEBENKOSTEN", tm_rows )
        x = self.getMieteinnahmenUndNebenkosten( master_name, jahr )
        self._createPreviewRowsFromMieteinnahme( x, tm_rows )
        self._createPreviewRowSeparator( "WERBUNGSKOSTEN", tm_rows )
        xwk = self.getWerbungskosten( master_name,jahr )
        self._createPreviewRowsFromWerbungskosten( xwk, tm_rows )
        # todo
        tm = AnlageVTableModel( tm_rows )
        return tm

    def _createPreviewRowsFromObjektdaten( self, master_name:str, gesamt_wfl:int, previewRows:List[PreviewRow] ) -> None:
        """
        Erzeugt PreviewRow-Objekte für den Master-Namen und die Gesamtwohnfläche
        :param master_name:
        :param gesamt_wfl:
        :param previewRows:
        :return:
        """
        r = PreviewRow()
        r.text = "Objekt"
        r.wert1 = master_name
        previewRows.append( r )

        o = self._getObjekt( master_name )
        zdef = self._getZeilenDef( "obj_str_hnr" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Lage des Objekts"
        r.wert1 = o.strasse_hnr
        previewRows.append( r )

        zdef = self._getZeilenDef( "gesamt_wfl" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Gesamtwohnfläche"
        r.wert1 = o.gesamt_wfl
        previewRows.append( r )

    def _createPreviewRowsFromMieteinnahme( self, x:XMieteinnahme, previewRows:List[PreviewRow] ) -> None:
        """
        Erzeugt PreviewRow-Objekte für Netto-Miete, NKV, NKA und hängt sie an die übergebene Liste der PreviewRows an.
        :param x:
        :param previewRows:
        :return:
        """
        r = PreviewRow()
        r.text = "Netto-Jahresmiete SOLL"
        r.wert1 = x.nettoSoll
        self._checkBemerkung( x.bemerkung, r )
        previewRows.append( r )

        zdef = self._getZeilenDef( "mieteinnahmen_netto" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "ME gesamtes Objekt ohne NK-Vorauszahlungen"
        r.wert2 = x.nettoMiete
        previewRows.append( r )

        r = PreviewRow()
        r.text = "NK-Vorauszahlungen"
        r.wert1 = x.nkv
        previewRows.append( r )

        r = PreviewRow()
        r.text = "Offene Erstattungen aus NKA"
        r.wert1 = x.offnNkErstattg
        previewRows.append( r )

        r = PreviewRow()
        r.text = "NK-Abrechnung aus VJ-1 (Rückzahlung: '-')"
        r.wert1 = x.nka
        previewRows.append( r )

        zdef = self._getZeilenDef( "umlagen" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "NKV saldiert mit NKA aus VJ-1"
        r.wert2 = self._getSaldoNebenkostenAusXMieteinnahme( x )
        previewRows.append( r )

        zdef = self._getZeilenDef( "summe_einnahmen" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Summe der Einnahmen"
        r.wert2 = self._getSummeEinnahmenAusXMieteinnahme( x )
        r.isSumme = True
        previewRows.append( r )

    def _createPreviewRowsFromWerbungskosten( self, x:XWerbungskosten, previewRows:List[PreviewRow] ) -> None:
        self._createPreviewRowsFromAfA( x.afa, previewRows )
        self._createPreviewRowSeparator( "", previewRows  )
        self._createPreviewRowsFromAufwandNichtVerteilt( x.erhalt_aufwand, x.jahr, previewRows )
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowsFromAufwandVerteilt( x.erhalt_aufwand_verteilt, x.jahr, previewRows )

    def _createPreviewRowsFromAfA( self, afa:XAfA, previewRows:List[PreviewRow] ) -> None:
        zdef = self._getZeilenDef( "afa_linear" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "AfA linear"
        r.wert1 = "X" if afa.afa_linear else ""
        previewRows.append( r )

        zdef = self._getZeilenDef( "afa_prozent" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "AfA Prozent"
        r.wert1 = afa.afa_prozent
        previewRows.append( r )

        zdef = self._getZeilenDef( "afa_wievorjahr" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "AfA wie Vorjahr"
        r.wert1 = "X" if afa.afa_wie_vorjahr else ""
        previewRows.append( r )

        zdef = self._getZeilenDef( "afa_betrag" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "AfA Betrag"
        r.wert2 = afa.afa
        previewRows.append( r )

    def _createPreviewRowsFromAufwandNichtVerteilt( self, aufwand:int, jahr:int, previewRows: List[PreviewRow] ) -> None:
        zdef = self._getZeilenDef( "kosten_voll_abziehbar" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "In %d voll abzuziehende Erhalt.Aufwendg." % (jahr)
        r.wert2 = aufwand
        r.isSumme = False
        previewRows.append( r )

    def _createPreviewRowsFromAufwandVerteilt( self, x:XAufwandVerteilt, jahr:int, previewRows: List[PreviewRow] ) -> None:
        zdef = self._getZeilenDef( "kosten_zu_verteilen" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Zu verteilender Gesamtaufwand in %d" % (jahr)
        r.wert1 = x.gesamt_aufwand_vj
        r.isSumme = False
        previewRows.append( r )

        # Zeile bleibt gleich
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "   davon in %d abzuziehen" % (jahr)
        r.wert2 = x.aufwand_vj
        r.isSumme = False
        previewRows.append( r )

        zdef = self._getZeilenDef( "anteil_aus_vj_minus_4" )
        teilaufwaende = [x.aufwand_vj_minus_1, x.aufwand_vj_minus_2, x.aufwand_vj_minus_3, x.aufwand_vj_minus_4]
        z = zdef.zeile
        for i in range( 4, 0, -1 ):
            r = PreviewRow()
            r.zeile = z
            z += 1
            r.text = "      zu berücksichtigen aus %d" % ( jahr - i )
            r.wert2 = teilaufwaende[i-1]
            r.isSumme = False
            previewRows.append( r )

    def _getSummeEinnahmenAusXMieteinnahme( self, x:XMieteinnahme ) -> int:
        return x.nettoMiete + self._getSaldoNebenkostenAusXMieteinnahme( x )

    def _getSaldoNebenkostenAusXMieteinnahme( self, x:XMieteinnahme ) -> int:
        return round( x.nkv + x.nka )

    def _checkBemerkung( self, bemerkung:str, row:PreviewRow ):
        if bemerkung:
            bem = row.bemerkung
            if bem:
                bem += " / "
            bem += bemerkung
            row.bemerkung = bem

    def _createPreviewRowSeparator( self, text:str, previewRows:List[PreviewRow] ):
        r = PreviewRow()
        r.text = text
        r.isSeparator = True
        previewRows.append( r )

    def _getJahresNettoSoll( self, master_name:str, jahr:int ) -> int:
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
        liefert alle Zeilen für den Druck der AnlageV des Objekts master_name (N_Stadtpark etc.)
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


###############
####################  A C H T u N G !!!!!!!!1  ###########################
################### TEST GEGEN TEST-DATENBANK !!!!!!!!!!1 ############
##############

def testPreview():
    app = QApplication()
    busi = AnlageV_Logic.inst()
    v = AnlageVView()
    v.setMinimumSize( 800, 1000 )
    tm = busi.createAnlageVTableModel( "SB_Kaiser", 2021 )
    v.setAnlageVTableModel( tm )
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

# def preview():
#     app = QApplication()
#     busi = AnlageV_Logic.inst()
#     zeilenlist = busi.getAnlageV_Zeilen( "BUEB_Saargemuend", 2021 )
#     busi.terminate()
#     avpreview = AnlageV_Preview( zeilenlist )
#     app.exec_()

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
    #preview()