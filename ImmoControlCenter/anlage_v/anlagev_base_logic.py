import os
from typing import List, Dict, Any

from anlage_v.anlagev_dataacess import AnlageV_DataAccess
from anlage_v.anlagev_interfaces import XObjektStammdaten, XAnlageV_Zeile, XZeilendefinition, XMieteinnahme, \
    XWerbungskosten, XAfA, XErhaltungsaufwand, XAufwandVerteilt, XAllgemeineKosten, XSammelAbgabeDetail, XAusgabeKurz
from constants import Zahlart, Sonstaus_Kostenart
from datehelper import getNumberOfMonths
from interfaces import XSollMiete


class AnlageV_Base_Logic:
    def __init__(self):
        self._db: AnlageV_DataAccess
        self._steuerpflichtiger:Dict = dict() #keys: name, vorname, steuerpflichtiger
        self._objektStammdatenList:List[XObjektStammdaten] = list()
        self._anlageV_zeilendefinitionen:List[XZeilendefinition] = list()
        self._prepare()

    def _prepare(self):
        path = os.getcwd()
        if "anlage_v" in path: # test des AnlageVControllers
            dbname = "../immo.db"
        else:
            dbname = "./immo.db" # Normaler Anwendungsstart
        #dbname = "/home/martin/Vermietung/ImmoControlCenter/immo.db"  # wenn im Test die Rel.-DB verwendet werden soll.
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

    def getJahre( self ) -> List[int]:
        return self._db.getJahre()

    def getObjekt( self, master_name:str ) -> XObjektStammdaten:
        for o in self._objektStammdatenList:
            if o.master_name == master_name: return o
        raise Exception( "AnlageV_Logic.getObjekt(): "
                         "Objekt '%s' nicht in der Objektliste gefunden." % (master_name) )

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
        x.nettoSoll = self.getJahresNettoSoll( master_name, jahr )
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
        x.erhalt_aufwand_verteilt = self.getVerteiltenErhaltungsaufwand( master_name, jahr )
        x.kostenart_a = self._db.getAusgabenSumme( master_name, jahr, Sonstaus_Kostenart.ALLGEMEIN )
        x.versicherungen = self._db.getAusgabenSumme( master_name, jahr, Sonstaus_Kostenart.VERSICHERUNG )
        x.grundsteuer = int( round( self._db.getAusgabenSumme( master_name, jahr, Sonstaus_Kostenart.GRUNDSTEUER ) ) )
        # bei einigen Objekten fehlen jetzt noch die Kosten, die von der Gemeinde
        # im Paket abgebucht wurden.
        # (Betrifft derzeit nur Gemeinden Neunkirchen und Ottweiler)
        # Diese jetzt ermitteln - dabei wird vorausgesetzt, dass in Tabelle sammelabgabe_detail wirklich nur solche
        # Sammelabbuchungen vorhanden sind. Sonst kommt es zu Doppelberechnungen.
        xsam:XSammelAbgabeDetail = self._db.getDetailFromSammelabgabe( master_name, jahr )
        if xsam:
            if x.grundsteuer == 0:
                x.grundsteuer = xsam.grundsteuer
            if x.strassenreinigung == 0:
                x.strassenreinigung = xsam.strassenreinigung
            if x.abwasser == 0:
                x.abwasser = xsam.abwasser

        x.allgemeine_kosten_gruppiert = self._getAllgemeinKostenBlockweise( master_name, jahr )
        # Sonstige Kosten (Hotelübernachtungen, Maklerprovisionen etc.)
        x.sonstige_kosten = self._db.getAusgabenSumme( master_name, jahr, Sonstaus_Kostenart.SONSTIGE )
        return x

    def _getAllgemeinKostenBlockweise( self, master_name:str, jahr:int ) -> List[XAusgabeKurz]:
        aus_grupp:List[XAusgabeKurz] = self._db.getAusgaben( master_name, jahr,
                                                             [Sonstaus_Kostenart.ALLGEMEIN,] )
                                                             # Sonstaus_Kostenart.GRUNDSTEUER,
                                                             # Sonstaus_Kostenart.VERSICHERUNG] )
        l:List[XAusgabeKurz] = list()
        block:XAusgabeKurz = None
        memo = ""
        for aus in aus_grupp:
            if memo != (aus.kostenart + aus.kreditor):
                block = XAusgabeKurz()
                l.append( block )
                block.master_name = master_name
                block.kostenart = aus.kostenart
                block.kreditor = aus.kreditor
                memo = aus.kostenart + aus.kreditor
            block.betrag += aus.betrag
        return l

    def getVerteiltenErhaltungsaufwand( self, master_name:str, jahr:int ) -> XAufwandVerteilt:
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

    def getUeberschuss( self, einn: XMieteinnahme, wk: XWerbungskosten ) -> int:
        summeEin = self.getSummeEinnahmenAusXMieteinnahme( einn )
        summeWk = wk.getSummeWerbungskosten()
        return int( round( summeEin + summeWk ) )  # "+", weil summeWk Ausgaben sind, also mit neg. Vorz. versehen.

    def getSummeEinnahmenAusXMieteinnahme( self, x:XMieteinnahme ) -> int:
        return int( round( x.nettoMiete + self.getSaldoNebenkostenAusXMieteinnahme( x ) ) )

    def getSaldoNebenkostenAusXMieteinnahme( self, x:XMieteinnahme ) -> int:
        return round( x.nkv + x.nka )

    def getJahresNettoSoll( self, master_name:str, jahr:int ) -> int:
        sollmieten: List[XSollMiete] = self.getSollmieten( master_name, jahr )
        nettoSoll = 0
        for sollmiete in sollmieten:
            nMonate = getNumberOfMonths( sollmiete.von, sollmiete.bis, jahr )
            nettoSoll += nMonate * sollmiete.netto
        return nettoSoll

    def getSollmieten( self, master_name, jahr:int ) -> List[XSollMiete]:
        return self._db.getSollmietenFuerMasterobjekt( master_name, jahr )

    def getObjektStammdatenList( self ) -> List[XObjektStammdaten]:
        return self._objektStammdatenList

    def getObjektNamen( self ) -> List[str]:
        """
        Liefert alle master_name aus der Tabelle masterobjekt,
        sortiert nach Name aufsteigend OHNE Namen wie "**alle**"
        :return:
        """
        #return self._db.getObjektNamen()
        return [obj.master_name for obj in self._objektStammdatenList]

    def getAllgemeineKosten( self, master_name:str, jahr:int ) -> List[XAllgemeineKosten]:
        kosten = self._db.getAllgemeineKosten( master_name, jahr )
        return kosten


# masterobjekte = [ "BUEB_Saargemuend", "HOM_Remigius",
#                   "ILL_Eich",
#                   "NK_Kleist", "NK_KuchenbergS", "NK_KuchenbergW", "NK_ThomasMann", "NK_Volkerstal",
#                   "NK_Ww224", "NK_Zweibrueck", "OTW_Linx", "OTW_Schwalbe", "RI_Lampennester",
#                   "SB_Charlotte", "SB_Gruelings", "SB_Hohenzoll", "SB_Kaiser" ]
masterobjekte = [ "ILL_Eich", "SB_Hohenzoll", "SB_Kaiser" ]

