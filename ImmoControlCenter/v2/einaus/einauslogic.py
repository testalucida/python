from typing import List

import datehelper
from v2.einaus.einausdata import EinAusData
from v2.icc.constants import iccMonthShortNames, EinAusArt, Umlegbar
from v2.icc.icclogic import IccTableModel, IccLogic
from v2.icc.interfaces import XEinAus

#################   EinAusTableModel   ############################
class EinAusTableModel( IccTableModel):
    def __init__( self, rowlist:List[XEinAus], jahr ):
        IccTableModel.__init__( self, rowlist, jahr )
        # keys = ( "ea_id", "master_name", "mobj_id", "debi_kredi", "jahr", "monat", "betrag", "ea_art", "verteilt_auf",
        #          "umlegbar", "buchungsdatum", "buchungstext", "mehrtext", "write_time" )
        # headers = ("ID", "Master", "Wohnung", "Debitor/\nKreditor", "Jahr", "Monat", "Betrag", "Art", "verteilt auf",
        #            "U", "Buchung am", "Buchg.text", "Mehr Text", "eingetragen" )
        # self.setKeyHeaderMappings2( keys, headers )
        self.setKeyHeaderMappings2(
            ("master_name", "mobj_id", "debi_kredi", "buchungstext", "buchungsdatum", "ea_art", "verteilt_auf",
             "betrag", "mehrtext", "write_time" ),
            ("Haus", "Whg", "Debitor/\nKreditor", "Buchungstext", "Buch.datum", "Art", "vJ",
             "Betrag", "Bemerkung", "eingetragen")
        )

#################   EinAusLogic   #################################
class EinAusLogic(IccLogic):
    """
    Beinhaltet die Logik, die für Operationen auf die Tabelle einaus notwendig ist.
    Verwendet EinAusData
    Wird verwendet z.B. von MtlEinAusLogic
    """
    def __init__( self ):
        IccLogic.__init__( self )
        self._einausData = EinAusData()

    def getZahlungenModel( self, jahr:int ) -> EinAusTableModel:
        """
        Liefert alle Ein- und Auszahlungen im Jahr <jahr> in Form eines EinAusTableModel.
        :param jahr:
        :return:
        """
        l:List[XEinAus] = self._einausData.getEinAuszahlungenJahr( jahr )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungenModel2( self, ea_art_display:str, jahr:int, monthIdx:int, mobj_id:str ) -> EinAusTableModel:
        month_sss = iccMonthShortNames[monthIdx]
        l: List[XEinAus] = self._einausData.getEinAuszahlungen2( ea_art_display, jahr, month_sss, mobj_id )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungenModel3( self, ea_art_display, jahr:int, monthIdx:int, debikredi:str ) -> EinAusTableModel:
        """
        :param ea_art:
        :param jahr:
        :param monthIdx:
        :param debikredi:
        :return:
        """
        month_sss = iccMonthShortNames[monthIdx]
        l: List[XEinAus] = self._einausData.getEinAuszahlungen3( ea_art_display, jahr, month_sss, debikredi )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungenModel4( self, sab_id:int, jahr:int, monthIdx:int ) -> EinAusTableModel:
        month_sss = iccMonthShortNames[monthIdx]
        l: List[XEinAus] = self._einausData.getEinAuszahlungen4( sab_id, jahr, month_sss )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungen( self, ea_art_display:str, jahr:int ) -> List[XEinAus]:
        """
        Liefert alle Zahlungen der Art <ea_art> im Jahr <jahr>
        :param ea_art_display:
        :param jahr:
        :return:
        """
        return self._einausData.getEinAusZahlungen( ea_art_display, jahr )

    def trySaveZahlung( self, x:XEinAus ) -> str:
        msg = self.validateZahlung( x )
        if msg:
            # Validierung nicht ok
            return msg
        else:
            # Validierung ok, jetzt speichern
            # ACHTUNG: eine Exception, die von _einausData geworfen wird, wird hier nicht abgefangen
            y, m, d = datehelper.getDateParts( x.buchungsdatum )
            x.jahr = y
            x.monat = iccMonthShortNames[m-1]
            if x.ea_id <= 0:
                self._einausData.insertEinAusZahlung( x )
                self._einausData.commit()
            else:
                self._einausData.updateEinAusZahlung( x )
                self._einausData.commit()
            return ""

    def validateZahlung( self, x:XEinAus ) -> str:
        """
        validiert die Daten einer Zahlung.
        :param x: XEinAus-Objekt, dessen Daten validiert werden sollen.
        :return: einen Leerstring, wenn alles in Ordnung ist, sonst eine Fehlermeldung.
        """
        if not x.debi_kredi:
            return "Kreditor oder Debitor fehlt."
        if not x.leistung:
            return "Leistung fehlt."
        if x.betrag == 0:
            return "Betrag fehlt."
        if x.ea_art == EinAusArt.REPARATUR.display:
            if not x.verteilt_auf:
                return "Bei Reparaturen muss angegeben werden, auf wieviele Jahre der Betrag verteilt werden soll."
        else:
            if x.verteilt_auf > 1:
                return "Verteilung auf Jahre darf nur bei Reparaturen angegeben werden."
        if not x.buchungsdatum:
            return "Buchungsdatum fehlt."
        return ""

    def addZahlung( self, ea_art, mobj_id:str, debikredi:str,
                    jahr:int, monthIdx:int, value:float,
                    buchungsdatum:str=None, buchungstext:str=None, mehrtext:str= None ) -> XEinAus:
        if buchungsdatum:
            if not datehelper.isValidIsoDatestring( buchungsdatum ):
                raise ValueError( "EinAusLogic.addZahlung():\nBuchungsdatum '%s' ist nicht im ISO-Format." )
        x = XEinAus()
        x.master_name = self._einausData.getMastername( mobj_id )
        x.mobj_id = mobj_id
        x.ea_art = ea_art
        x.debi_kredi = debikredi
        x.jahr = jahr
        x.monat = iccMonthShortNames[monthIdx]
        x.betrag = value
        x.verteilt_auf = None
        x.buchungstext = buchungstext
        x.buchungsdatum = buchungsdatum
        x.mehrtext = mehrtext
        # todo: Methode trySaveZahlung verwenden
        self._einausData.insertEinAusZahlung( x )
        return x

    def addZahlung2( self, ea_art_display, master_name:str,  mobj_id:str, debikredi:str, sab_id:int,
                    jahr:int, monthIdx:int, value:float, umlegbar:str=Umlegbar.NEIN.value,
                    buchungsdatum:str=None, buchungstext:str=None, mehrtext:str= None ) -> XEinAus:
        if buchungsdatum:
            if not datehelper.isValidIsoDatestring( buchungsdatum ):
                raise ValueError( "EinAusLogic.addZahlung():\nBuchungsdatum '%s' ist nicht im ISO-Format." )
        x = XEinAus()
        x.master_name = master_name
        x.mobj_id = mobj_id
        x.ea_art = ea_art_display
        x.debi_kredi = debikredi
        x.sab_id = sab_id
        x.jahr = jahr
        x.monat = iccMonthShortNames[monthIdx]
        x.betrag = value
        x.verteilt_auf = None
        x.umlegbar = umlegbar
        x.buchungstext = buchungstext
        x.buchungsdatum = buchungsdatum
        x.mehrtext = mehrtext
        # todo: Methode trySaveZahlung verwenden
        self._einausData.insertEinAusZahlung( x )
        return x

    def updateZahlung( self, x:XEinAus ) -> int:
        # todo: Methode trySaveZahlung verwenden
        rowsAffected = self._einausData.updateEinAusZahlung( x )
        return rowsAffected

    def deleteZahlungen( self, xlist:List[XEinAus] ):
        for x in xlist:
            self._einausData.deleteEinAusZahlung( x.ea_id )

    def commit( self ):
        self._einausData.commit()

    def rollback( self ):
        self._einausData.rollback()