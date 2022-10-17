from typing import List

import datehelper
from v2.einaus.einausdata import EinAusData
from v2.icc.constants import iccMonthShortNames, EinAusArt
from v2.icc.icclogic import IccTableModel, IccLogic
from v2.icc.interfaces import XEinAus

#################   EinAusTableModel   ############################
class EinAusTableModel( IccTableModel):
    def __init__( self, rowlist:List[XEinAus], jahr ):
        IccTableModel.__init__( self, rowlist, jahr )
        keys = ( "ea_id", "master_name", "mobj_id", "debi_kredi", "jahr", "monat", "betrag", "ea_art", "verteilt_auf",
                 "umlegbar", "buchungsdatum", "buchungstext", "mehrtext", "write_time" )
        headers = ("ID", "Master", "Wohnung", "Debitor/\nKreditor", "Jahr", "Monat", "Betrag", "Art", "verteilt auf",
                   "U", "Buchung am", "Buchg.text", "Mehr Text", "eingetragen" )
        self.setKeyHeaderMappings2( keys, headers )

#################   EinAusLogic   #################################
class EinAusLogic(IccLogic):
    """
    Beinhaltet die Logik, die für Operationen auf die Tabelle einaus notwendig ist.
    Verwendet EinAusData
    Wird verwendet z.B. von MtlEinAusLogic
    """
    def __init__( self ):
        self._einausData = EinAusData()

    def getZahlungenModel( self, jahr:int ) -> EinAusTableModel:
        l:List[XEinAus] = self._einausData.getEinAuszahlungenJahr( jahr )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungenModel2( self, ea_art, jahr:int, monthIdx:int, mobj_id:str ) -> EinAusTableModel:
        month_sss = iccMonthShortNames[monthIdx]
        l: List[XEinAus] = self._einausData.getEinAuszahlungen2( ea_art, jahr, month_sss, mobj_id )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungenModel3( self, ea_art, jahr:int, monthIdx:int, mv_id:str ) -> EinAusTableModel:
        month_sss = iccMonthShortNames[monthIdx]
        l: List[XEinAus] = self._einausData.getEinAuszahlungen3( ea_art, jahr, month_sss, mv_id )
        for x in l:
            x.write_time = x.write_time[0:10]
        tm = EinAusTableModel( l, jahr )
        return tm

    def getZahlungen( self, ea_art:EinAusArt, jahr:int ) -> List[XEinAus]:
        return self._einausData.getEinAusZahlungen( ea_art.value[0], jahr )

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
        x.buchungstext = buchungstext
        x.buchungsdatum = buchungsdatum
        x.mehrtext = mehrtext
        ea_id = self._einausData.insertEinAusZahlung( x )
        x.ea_id = ea_id
        return x

    def updateZahlung( self, x:XEinAus ) -> int:
        rowsAffected = self._einausData.updateEinAusZahlung( x )
        return rowsAffected

    def deleteZahlungen( self, xlist:List[XEinAus] ):
        for x in xlist:
            self._einausData.deleteEinAusZahlung( x.ea_id )

    def commit( self ):
        self._einausData.commit()

    def rollback( self ):
        self._einausData.rollback()