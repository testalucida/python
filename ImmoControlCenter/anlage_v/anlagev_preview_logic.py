from typing import List, Dict, Any

from PySide2.QtWidgets import QApplication

from anlage_v.anlagev_base_logic import AnlageV_Base_Logic

from anlage_v.anlagev_interfaces import XObjektStammdaten, XAnlageV_Zeile, XZeilendefinition, XMieteinnahme, \
    XWerbungskosten, XAfA, XErhaltungsaufwand, XAufwandVerteilt, XAllgemeineKosten
# from anlage_v.anlagev_preview import AnlageV_Preview
# import numbers

from anlage_v.anlagev_tablemodel import AnlageVTableModel, PreviewRow
from anlage_v.anlagev_view import AnlageVView
# from constants import Zahlart
# from datehelper import getNumberOfMonths
# from interfaces import XSollMiete, XSonstAus


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
        # ueber = self._getSummeEinnahmenAusXMieteinnahme( einn ) + summeWk
        ueber = self._getUeberschuss( einn, xwk )
        self._createPreviewRowFromUeberschuss( self._getSummeEinnahmenAusXMieteinnahme( einn ), summeWk, ueber,
                                               tm_rows )
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
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowFromAllgemeineKosten( x.allgemeine_kosten, previewRows )
        self._createPreviewRowSeparator( "", previewRows )
        self._createPreviewRowFromSonstigeKosten( x.sonstige_kosten, previewRows )

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
    v = AnlageVView()
    v.setMinimumSize( 1000, 1100 )
    tm = busi.getAnlageVTableModel( "OTW_Linx", 2021 )
    v.setAnlageVTableModel( tm )
    v.show()
    app.exec_()

if __name__ == "__main__":
    testPreview()
