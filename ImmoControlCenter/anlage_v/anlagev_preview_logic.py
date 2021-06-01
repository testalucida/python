from typing import List
from PySide2.QtWidgets import QApplication

from anlage_v.ausgabenmodel import AusgabenModel
from anlage_v.anlagev_base_logic import AnlageV_Base_Logic
from anlage_v.anlagev_interfaces import XMieteinnahme, \
    XWerbungskosten, XAfA, XAufwandVerteilt, XAusgabeKurz, XVerteilterAufwand, XErhaltungsaufwand
from anlage_v.anlagev_tablemodel import AnlageVTableModel, PreviewRow
from constants import Sonstaus_Kostenart, DetailLink


class AnlageV_Preview_Logic( AnlageV_Base_Logic):
    def __init__(self):
        AnlageV_Base_Logic.__init__( self )

    def getAnlageVTableModel( self, master_name: str, jahr: int ) -> AnlageVTableModel:
        """
        TableModel für die AnlageV-Preview in einer QTableView
        :param master_name:
        :param jahr:
        :return:
        """
        tm_rows: List[PreviewRow] = list()
        x = self.getObjekt( master_name )
        self._createPreviewRowsFromObjektdaten( master_name, x.gesamt_wfl, tm_rows )
        self._createPreviewRowSeparator( "EINNAHMEN und NEBENKOSTEN", tm_rows )
        einn = self.getMieteinnahmenUndNebenkosten( master_name, jahr )
        self._createPreviewRowsFromMieteinnahme( einn, tm_rows )
        self._createPreviewRowSeparator( "WERBUNGSKOSTEN", tm_rows )
        xwk = self.getWerbungskosten( master_name, jahr )
        self._createPreviewRowsFromWerbungskosten( xwk, tm_rows )
        summeWk = xwk.getSummeWerbungskosten()
        self._createPreviewRowFromSummeWk( summeWk, tm_rows )
        self._createPreviewRowSeparator( "ÜBERSCHUSS", tm_rows )
        ueber = self.getUeberschuss( einn, xwk )
        self._createPreviewRowFromUeberschuss( self.getSummeEinnahmenAusXMieteinnahme( einn ), summeWk, ueber, tm_rows )
        tm = AnlageVTableModel( master_name, jahr, tm_rows )
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

        o = self.getObjekt( master_name )
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
        r.wert2 = int( round( x.nettoMiete ) )
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
        r.wert2 = int( round( self.getSaldoNebenkostenAusXMieteinnahme( x ) ) )
        previewRows.append( r )

        zdef = self._getZeilenDef( "summe_einnahmen" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Summe der Einnahmen"
        r.wert2 = int( round( self.getSummeEinnahmenAusXMieteinnahme( x ) ) )
        r.isSumme = True
        previewRows.append( r )

    def _createPreviewRowsFromWerbungskosten( self, x:XWerbungskosten, previewRows:List[PreviewRow] ) -> None:
        self._createPreviewRowsFromAfA( x.afa, previewRows )
        self._createPreviewRowSeparator( "", previewRows  )
        self._createPreviewRowsFromAufwandNichtVerteilt( x.erhalt_aufwand, x.jahr, previewRows )
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowsFromAufwandVerteilt( x.erhalt_aufwand_verteilt, x.jahr, previewRows )
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowsFromAllgemeineKostenDetailliert(
            x.grundsteuer, x.abwasser, x.strassenreinigung, x.allgemeine_kosten_gruppiert, previewRows )
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowFromAllgemeineKosten( int( round( x.getSummeAllgemeineKosten() ) ), previewRows )
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowFromSonstigeKosten( int( round( x.sonstige_kosten ) ), previewRows )

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

        zdef = self._getZeilenDef( "afa_wie_vorjahr" )
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
        r.detailLink = DetailLink.ERHALTUNGSKOSTEN.value[0]
        r.wert2 = aufwand
        r.isSumme = False
        previewRows.append( r )

    def _createPreviewRowsFromAufwandVerteilt( self, x:XAufwandVerteilt, jahr:int, previewRows: List[PreviewRow] ) -> None:
        zdef = self._getZeilenDef( "kosten_zu_verteilen" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Zu verteilender Gesamtaufwand in %d" % (jahr)
        r.detailLink = DetailLink.ZU_VERTEIL_GESAMTKOSTEN_VJ.value[0]
        r.wert1 = x.gesamt_aufwand_vj
        r.isSumme = False
        previewRows.append( r )

        # Zeile bleibt gleich
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "   davon in %d abzuziehen" % (jahr)
        r.detailLink = DetailLink.ERHALTUNGSKOSTEN_VERTEILT.value[0]
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

    def _createPreviewRowsFromAllgemeineKostenDetailliert( self, grundsteuer:int, abwasser:int, strassenreinigung:int,
                                                           ausgaben:List[XAusgabeKurz], previewRows: List[PreviewRow] ) -> None:
        r = PreviewRow()
        r.text = "Auflistung allg. Kosten: Grundsteuer, Vers., Müll, Abwasser, Str.reinigg. - summiert auf Kreditoren"
        r.detailLink = DetailLink.ALLGEMEINE_KOSTEN.value[0]
        previewRows.append( r )
        indent = "   "
        summe = 0

        if grundsteuer != 0:
            summe += grundsteuer
            r = PreviewRow()
            r.text = indent + "Grundsteuer " + "(g)"
            r.wert1 = grundsteuer
            r.isSumme = False
            previewRows.append( r )
        if abwasser != 0:
            summe += abwasser
            r = PreviewRow()
            r.text = indent + "Abwasser " + "(a)"
            r.wert1 = abwasser
            r.isSumme = False
            previewRows.append( r )
        if strassenreinigung != 0:
            summe += strassenreinigung
            r = PreviewRow()
            r.text = indent + "Straßenreinigung " + "(a)"
            r.wert1 = strassenreinigung
            r.isSumme = False
            previewRows.append( r )

        for aus in ausgaben:
            r = PreviewRow()
            r.text = indent + aus.kreditor + " (" + aus.kostenart + ")"
            r.wert1 = aus.betrag
            summe += aus.betrag
            r.isSumme = False
            previewRows.append( r )
        r = PreviewRow()
        zdef = self._getZeilenDef( "hauskosten_allg" )
        r.text = "       SUMME dieser Posten: " + str( int( round( summe ) ) ) + " Euro >> zu übertragen in Zeile " + \
                 str( zdef.zeile )
        previewRows.append( r )

    def _createPreviewRowFromAllgemeineKosten( self, allgKosten:int, previewRows: List[PreviewRow] ) -> None:
        zdef = self._getZeilenDef( "hauskosten_allg" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Grundsteuer, Str.reinigg, Müllabfuhr, Allg.strom etc"
        r.wert2 = allgKosten
        r.isSumme = False
        previewRows.append( r )

    def _createPreviewRowFromSonstigeKosten( self, sonstKosten:int, previewRows: List[PreviewRow] ) -> None:
        zdef = self._getZeilenDef( "sonstige_kosten" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Sonstige Kosten: Übernachtungen, Post, Provisionen, ..."
        r.wert2 = sonstKosten
        r.isSumme = False
        previewRows.append( r )

    def _createPreviewRowFromSummeWk( self, summeWk: int, previewRows: List[PreviewRow] ):
        zdef = self._getZeilenDef( "summe_werbungskosten" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Summe der Werbungskosten (zu übertragen nach Zeile 22)"
        r.wert2 = summeWk
        r.isSumme = True
        previewRows.append( r )

    def _createPreviewRowFromUeberschuss( self, einnahme:int, summeWk:int, ueber:int, previewRows: List[PreviewRow] ):
        zdef = self._getZeilenDef( "ueberschuss" )
        r = PreviewRow()
        r.zeile = zdef.zeile
        r.text = "Überschuss (Saldo Einnahmen %d und Werbungskosten %d)" % (einnahme, summeWk )
        r.wert2 = ueber
        r.isSumme = True
        previewRows.append( r )

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

    def getAllgemeineAusgabenModel( self, master_name:str, jahr:int ) -> AusgabenModel:
        l:List[XAusgabeKurz] = self._db.getAusgaben( master_name, jahr, [Sonstaus_Kostenart.GRUNDSTEUER,
                                                                          Sonstaus_Kostenart.ALLGEMEIN,
                                                                          Sonstaus_Kostenart.VERSICHERUNG] )
        tm:AusgabenModel = AusgabenModel( master_name, jahr, l )
        tm.setHeaders( ["Kreditor", "Wohng", "Buchungstext", "Buch.datum", "Kostenart", "Betrag", "Summe"] )
        tm.setKeys( ["kreditor", "mobj_id", "buchungstext", "buchungsdatum", "kostenart", "betrag", ""] )
        tm.addColumnFunction( 6, self.getKreditorSumme )
        return tm

    def getReparaturausgabenNichtVerteilt( self, master_name:str, jahr:int ) -> AusgabenModel:
        l: List[XAusgabeKurz] = self._db.getAusgaben( master_name, jahr, [Sonstaus_Kostenart.REPARATUR,] )
        tm:AusgabenModel = AusgabenModel( master_name, jahr, l )
        tm.setHeaders( ["Kreditor", "Wohng", "Buchungstext", "Buch.datum", "Kostenart", "Betrag", "Summe"] )
        tm.setKeys( ["kreditor", "mobj_id", "buchungstext", "buchungsdatum", "kostenart", "betrag", ""] )
        tm.addColumnFunction( 6, self.getKreditorSumme )
        return tm

    def getReparaturausgabenVerteilt( self, master_name:str, jahr:int ) -> AusgabenModel:
        l: List[XErhaltungsaufwand] = self._db.getVerteilteErhaltungsaufwendungen( master_name, jahr )
        for x in l:
            x.betrag = int( round( x.betrag / x.verteilen_auf_jahre ) )
        tm:AusgabenModel = AusgabenModel( master_name, jahr, l )
        tm.setHeaders( ["Jahr", "Kreditor", "Whg", "Buch.Text", "Betrag", "Summe"] )
        tm.setKeys( ["buchungsjahr", "kreditor", "mobj_id", "buchungstext", "betrag", ""] )
        tm.addColumnFunction( 5, self.getJahressumme )
        return tm

    def getZuVerteilendeAufwaende( self, master_name:str, jahr:int ) -> AusgabenModel:
        """
        Liefert die Aufwände, die in <jahr> neu hinzugekommen und zu verteilen sind.
        :param master_name:
        :param jahr:
        :return:
        """
        awlist: List[XErhaltungsaufwand] = self._db.getZuVerteilendeAufwaendeVJ( master_name, jahr )
        tm:AusgabenModel = AusgabenModel( master_name, jahr, awlist )
        tm.setHeaders( ["Jahr", "Kreditor", "Whg", "Buch.Text", "Betrag", "Summe"] )
        tm.setKeys( ["buchungsjahr", "kreditor", "mobj_id", "buchungstext", "betrag", ""] )
        tm.addColumnFunction( 5, self.getJahressumme )
        return tm

    def getJahressumme( self, tm:AusgabenModel, row:int, col:int ) -> int:
        """
        Callback function für AusgabenModel
        :param tm:
        :param row:
        :param col:
        :return:
        """
        j = tm.getValue( row, 0 )
        nextj = tm.getValue( row + 1, 0 )
        if nextj is None or nextj != j:
            sum = 0
            startrow = tm.getStartRow( j, row, 0 )
            for r in range( startrow, row + 1 ):
                sum += tm.getValue( r, 4 )
            return sum
        return None

    def getKreditorSumme( self, tm:AusgabenModel, indexrow: int, indexcolumn:int ) -> float or None:
        """
        Callback function für AusgabenModel
        Prüfen, ob ein Gruppenwechsel bezüglich Kreditor bevorsteht.
        Wenn ja, Summe des vorausgehenden Kreditors berechnen.
        Wenn nein, nichts zurückgeben.
        :param indexrow:
        :return:
        """
        thisKreditor = tm.getValue( indexrow, 0 )
        nextKreditor = tm.getValue( indexrow + 1, 0 )
        if nextKreditor is None or nextKreditor != thisKreditor:
            sum = 0
            startrow = tm.getStartRow( thisKreditor, indexrow, 0 )
            for r in range( startrow, indexrow + 1 ):
                sum += tm.getValue( r, 5 )
            return sum
        return None

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
    busi = AnlageV_Preview_Logic()
    # v = AnlageVView()
    # v.setMinimumSize( 1000, 1100 )
    # tm = busi.getAnlageVTableModel( "SB_Kaiser", 2021 )
    # v.setAnlageVTableModel( tm )
    #v.show()
    app.exec_()

if __name__ == "__main__":
    testPreview()
