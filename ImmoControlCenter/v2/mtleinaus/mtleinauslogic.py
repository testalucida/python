from abc import abstractmethod
from typing import List, Any, Iterable

from PySide2.QtGui import QBrush, Qt

import datehelper
from base.basetablemodel import BaseTableModel
from v2.einaus.einausdata import EinAusData
from v2.einaus.einauslogic import EinAusTableModel, EinAusLogic
from v2.icc import constants
from v2.icc.constants import EinAusArt, iccMonthShortNames
from v2.icc.iccdata import IccData
from v2.icc.icclogic import IccSumTableModel, IccTableModel, IccLogic
from v2.icc.interfaces import XMtlZahlung, XEinAus, XMietverhaeltnisKurz, XSollMiete
from v2.mtleinaus.mietedata import MieteData

###############  MieteTableModel  #############
class MtlEinAusTableModel( IccSumTableModel ):
    """
    TableModel, das für die monatlichen Mieteinzahlungen und monatlichen Hausgeldauszahlungen verwendet wird.
    """
    def __init__( self, rowList:List[XMtlZahlung], jahr:int, editablemonthIdx:int, colsToSum:Iterable[str] ):
        """
        :param rowList: Liste mit XBase-Objekten. Jedes XBase-Objekt wird in der TableView durch eine Row repräsentiert.
        :param jahr:
        :param editablemonthIdx: Repräsentiert den Index des Monats, dessen Monatswert nach dem Klicken auf die OK-Spalte
                                 geändert wird. 0=Januar, 11=Dezember
        :param colsToSum: Zu summierende Spalten
        """
        IccSumTableModel.__init__( self, rowList, jahr, colsToSum )
        self._okBrush = QBrush( Qt.green )
        self._nokBrush = QBrush( Qt.red )
        self._editBrush = QBrush( Qt.yellow )
        self._idxOkColumn = 3
        self._idxNokColumn = 4
        self._idxSollColumn = 2
        self._idxJanuarColumn = 5
        self._idxEditableColumn = self._idxJanuarColumn + editablemonthIdx
        self.setKeyHeaderMappings2(
            ("mobj_id", self.getDebiKrediKey(), "soll", "ok", "nok", "jan", "feb", "mrz", "apr", "mai", "jun", "jul", "aug",
             "sep", "okt", "nov", "dez", "summe"),
            ("Objekt", self.getDebiKrediHeader(), "Soll", "ok", "nok", "Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug",
             "Sep", "Okt", "Nov", "Dez", "Summe") )
        self._idxSumColumn = self.getColumnIndexByKey( "summe" )

    @abstractmethod
    def getDebiKrediKey( self ) -> str:
        pass

    @abstractmethod
    def getDebiKrediHeader( self ) -> str:
        pass

    def getMietobjekt( self, row:int ) -> str:
        objIdx = self.keys.index( "mobj_id" )
        return self.getValue( row, objIdx )

    def getDebiKredi( self, row ) -> str:
        colIdx = self.keys.index( self.getDebiKrediKey() )
        return self.getValue( row, colIdx )

    def setValue( self, row:int, col:int, value:float ) -> None:
        """
        Setzt einen Monatswert und korrigiert die Summe entsprechend.
        Annahme hierbei: vom User können in dieser Tabelle ausschließlich Monatswerte geändert werden.
        Überschreibt die Methode der Basisklasse, weil nach einer Änderung eines Monatswerts
        auch der Summenwert angepasst werden muss. Es finden hier also 2 Aufrufe von BaseTableModel.setValue() statt.
        :param row: Row-Index der zu ändernden Zelle
        :param col: Column-Index der zu ändernden Zelle
        :param value: Neuer Wert
        :return: None
        """
        oldval = self.getValue( row, col )
        delta = value - oldval
        super().setValue( row, col, value )
        oldSum = self.getValue( row, self._idxSumColumn )
        newSum = oldSum + delta
        super().setValue( row,self._idxSumColumn, newSum )

    def getSummeValue( self, row:int ) -> float:
        return self.getValue( row, self._idxSumColumn )

    def getSollValue( self, row: int ) -> float:
        return self.getValue( row, self._idxSollColumn )

    def internalGetValue( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexcolumn in (self._idxOkColumn, self._idxNokColumn):
            return None
        else:
            return super().internalGetValue( indexrow, indexcolumn )

    def getSollColumnIdx( self ) -> int:
        return self._idxSollColumn

    def getJanuarColumnIndex( self ) -> int:
        return self._idxJanuarColumn

    def getOkColumnIdx( self ) -> int:
        return self._idxOkColumn

    def getNokColumnIdx( self ) -> int:
        return self._idxNokColumn

    def setEditableMonth( self, monthIdx:int ):
        oldEditIdx = self._idxEditableColumn
        self._idxEditableColumn = self._idxJanuarColumn + monthIdx
        idxA = self.createIndex( 0, oldEditIdx )
        idxE = self.createIndex( self.rowCount()-1, oldEditIdx )
        self.dataChanged.emit( idxA, idxE, [Qt.BackgroundColorRole] )
        idxA = self.createIndex( 0, self._idxEditableColumn )
        idxE = self.createIndex( self.rowCount()-1, self._idxEditableColumn )
        self.dataChanged.emit( idxA, idxE, [Qt.BackgroundColorRole] )

    def getSelectedMonthIdx( self ) -> int:
        """
        Liefert den Index des Monats, der zur Bearbeitung ausgewählt ist (0=Januar,...)
        :return:
        """
        return self._idxEditableColumn - self._idxJanuarColumn

    def getSelectedYear( self ) -> int:
        """
        Liefert das Jahr, das zur Bearbeitung ausgewählt ist
        :return:
        """
        return self.getJahr()

    def getEditableColumnIdx( self ) -> int:
        """
        liefert den Index der Spalte, die den bearbeitbaren Monat repräsentiert
        :return:
        """
        return self._idxEditableColumn

    def getEditableMonthIdx( self ) -> int:
        return self._idxEditableColumn - self._idxJanuarColumn

    def getBackgroundBrush( self, indexrow: int, indexcolumn: int ) -> QBrush or None:
        if indexrow == self.rowCount() - 1: return
        if indexcolumn == self._idxOkColumn:
            return self._okBrush
        elif indexcolumn == self._idxNokColumn:
            return self._nokBrush
        elif indexcolumn == self._idxEditableColumn:
            return self._editBrush
        #todo: den Diagonal-Brush einbauen, wenn das Mietverhältnis im betreff. Monat nicht aktiv war
        return None

###############  MieteTableModel  #############
class MieteTableModel( MtlEinAusTableModel ):
    def __init__( self, rowList:List[XMtlZahlung], jahr:int, editableMonthIdx:int ):
        MtlEinAusTableModel.__init__( self, rowList, jahr, editableMonthIdx, ( "soll", "summe" ) )

    def getDebiKrediKey( self ) -> str:
        return "mv_id"

    def getDebiKrediHeader( self ) -> str:
        return "Mieter"

################  MtlEinAusLogic  ############################
class MtlEinAusLogic( IccLogic ):
    """
    Beinhaltet die Logik, die für die Zusammenstellung der Daten notwendig ist, die in den Miet- und Hausgeldzahlungs-
    TableViews angezeigt werden.
    Konkret: in der Tabelle einaus gibt es nur einzelne Zahlungen. Für die Anzeige in der Miet- u. HG-Tableview
    müssen aber Monatswerte angezeigt werden, welche sich möglicherweise aus mehreren Einzelzahlungen zusammensetzen.
    MtlEinAusLogic bzw. ihre erbenden Klassen sind dafür verantwortlich, die Einzelzahlungen auf Monatswerte zu
    verdichten.
    Stellt abstrakte Methoden bereit, die von den erbenden Klassen MieteLogic und HausgeldLogic implementiert werden
    müssen.
    """
    def __init__( self ):
        #self.einausData = EinAusData()
        pass

    @abstractmethod
    def getEinAusArt( self ) -> EinAusArt:
        pass

    def addMonatsZahlung( self, mobj_id:str, debikredi:str, selectedYear:int, selectedMonth:int, value:float, text:str= "" ):
        ealogic = EinAusLogic()
        ealogic.addZahlung( self.getEinAusArt(), mobj_id, debikredi, selectedYear, selectedMonth, value, text )

    def getZahlungenModelObjektMonat( self, mobj_id, year:int, monthIdx:int ) -> EinAusTableModel:
        ea_art = self.getEinAusArt()
        ealogic = EinAusLogic()
        return ealogic.getZahlungenModel2( ea_art, year, monthIdx, mobj_id )


#####################  MtlMieteLogic SINGLETON  ############################
class MieteLogic( MtlEinAusLogic ):
    __instance = None
    def __init__( self ):
        if MieteLogic.__instance:
            raise Exception( "You can't instantiate MieteLogic more than once." )
        else:
            MtlEinAusLogic.__init__( self ) # call to super class
            self._mieteData = MieteData()
            MieteLogic.__instance = self

    @staticmethod
    def inst() -> __instance:
        if not MieteLogic.__instance:
            MieteLogic()
        return MieteLogic.__instance

    def getEinAusArt( self ) -> EinAusArt:
        return EinAusArt.BRUTTOMIETE.value[0]

    def getMietzahlungenModel( self, jahr: int, checkmonatIdx:int=None ) -> MieteTableModel:
        l:List[XMtlZahlung] = self.getMietzahlungen( jahr, checkmonatIdx )
        tm = MieteTableModel( l, jahr, checkmonatIdx )
        return tm

    def getMietzahlungen( self, jahr: int, checkmonatIdx:int=None ) -> List[XMtlZahlung]:
        """
        Liefert eine Liste aller gezahlten Monatsmieten aller Mieter in <jahr>
        Hat ein Mieter in einem Monat mehrere Teilbeträge bezahlt, werden diese in 1 XMtlZahlung-Objekt verdichtet.
        :param jahr: Jahr, für das die Mietzahlungen zu ermitteln sind
        :param checkmonatIdx: Der Index des Monats - BEGINNEND BEI 0 -,
        der zur Bearbeitung ausgewählt ist. Für diesen Monat werden die Sollmieten in
                         der UI-Tabelle angezeigt.
        :return:
        """
        ealogic = EinAusLogic()
        einausList: List[XEinAus] = ealogic.getZahlungen( EinAusArt.BRUTTOMIETE, jahr )
        # Annahme: in einausList können mehrere Zahlungsvorgänge eines Debitors/Kreditors sein, die den gleichen Monat
        # betreffen.
        # Deshalb muss die einausList zunächst auf Monate verdichtet werden,
        # und vor dem Verdichten wird sie nach Mietern (Debitoren) sortiert.
        einausList = self._getCondensedEinAusList( einausList )
        # einausList enthält nun je Mieter (Debitor) und Monat ein XEinAus-Objekt und ist nach Mietern sortiert.
        # Nicht für jeden Monat muss ein XEinAus-Objekt vorhanden sein.

        # Die Liste der XEinAus-Objekte muss nun in eine Liste von XMtlZahlung-Objekte umgewandelt werden (für das
        # TableModel).
        # Dafür müssen wir zuerst eine Liste der in <jahr> aktiven Mietverhältnisse holen:
        mvlist: List[XMietverhaeltnisKurz] = self._getUniqueMietverhaeltnisse( jahr )
        # je XMietverhaeltnisKurz-Objekt in mvlist ein XMtlZahlung-OBjekt anlegen und in die XMtlZahlung-Liste packen:
        mzlist:List[XMtlZahlung] = self._convertMietVhToMtlZahlg( mvlist, jahr )
        # die XMtlZahlung-Objekte in mzlist müssen jetzt noch mit den Zahlungsdaten versorgt werden:
        self._provideZahlungen( mzlist, einausList )
        self.provideSollMieten( jahr, constants.iccMonthShortNames[checkmonatIdx], mzlist )
        return mzlist

    def provideSollMieten( self, jahr:int, monat:str, mzlist:List[XMtlZahlung] ) -> List[XMtlZahlung]:
        """
        Arbeitet in <mzlist> die Monats-Sollwerte des Monats <jahr>/<monat> ein.
        Wird benötigt, wenn im UI der Monat umgestellt wird.
        Jedes XMtlZahlung-Objekt entspricht einer Zeile in der UI-Tabelle.
        :param jahr:
        :param monat: gem. iccMonthShortNames
        :param mzlist: die Liste mit XMtlZahlung-Objekten, die mit den Sollwerten für <jahr>/<monat> aktualisiert werden soll
        :return: die aktualisierte <mzlist>
        """
        monatIdx = iccMonthShortNames.index( monat )
        smlist: List[XSollMiete] = self.getSollMieten( jahr, monatIdx )
        for mz in mzlist:
            for sm in smlist:
                if sm.mv_id == mz.mv_id and sm.mobj_id == mz.mobj_id:
                    mz.soll = sm.brutto
                    break
        return mzlist

    def getSollMieten( self, jahr: int, monatIdx:int ) -> List[XSollMiete]:
        """
        Liefert alle Sollmieten, die im Jahr <jahr> und Monat <monat> gültig waren.
        Annahme: Sollmieten ändern sich ausschließlich zum 1. eines Moants
        :param jahr:
        :param monatIdx: Monatsindex. Januar = 0, Dezember = 11
        :return:
        """
        check = "%d-%02d-%02d" % (jahr, monatIdx+1, 1)
        l:List[XSollMiete] = self._mieteData.getSollmieten( jahr )
        retlist:List[XSollMiete] = list()
        for x in l:
            if datehelper.isWithin( check, x.von, x.bis ):
                retlist.append( x )
        return retlist

    def _convertMietVhToMtlZahlg( self, mvlist: List[XMietverhaeltnisKurz], jahr: int ) -> List[XMtlZahlung]:
        def getMonthIntervallForCurrentYear( isoVon: str, isoBis: str ) -> (str, str):
            """
            Ermittelt, ob der Zeitraum isoVon bis isoBis das komplette <jahr> beinhaltet (dann wird ("jan", "dez") zurück-
            gegeben) oder ob isoVon erst in <jahr> startet (dann wird der Monatsname des entsprechenden Startmonats
            zurückgegeben) oder ob isoBis in <jahr> fällt (dann wird der Monatsname des entsprechenden Endemonats
            zurückgegeben).
            Beispiel: isoVon = 2021-05-01, isoBis = NULL bzw. NONE, jahr = 2022.
                      Zurückgegeben wird ("jan", "dez")
            :param isoVon: Datum, ab wann ein MV existiert
            :param isoBis: Datum, bis wann ein MV existiert (hat) bzw. None
            :return: Tuple mit 2 Strings (Monatsnamen wie "jan", "dez",...)
            """
            vonY, vonM, vonD = datehelper.getDateParts( isoVon )
            if isoBis:
                bisY, bisM, bisD = datehelper.getDateParts( isoBis )
            else:
                isoBis = "2099-12-31"
                bisY, bisM, bisD = 2099, 12, 31
            if bisY < jahr:
                raise Exception( "getMonthIntervallForGivenYear():\nisoBis endet vor <jahr> %d" % jahr )

            firstMon, lastMon = "", ""
            if datehelper.isWithin( isoVon, jahrStart, jahrEnd ):
                firstMon = iccMonthShortNames[vonM - 1]
            else:
                firstMon = iccMonthShortNames[0]
            if datehelper.isWithin( isoBis, jahrStart, jahrEnd ):
                lastMon = iccMonthShortNames[bisM - 1]
            else:
                lastMon = iccMonthShortNames[11]
            return firstMon, lastMon

        jahrStart = str( jahr ) + "-01-01"
        jahrEnd = str( jahr ) + "-12-31"
        mzlist: List[XMtlZahlung] = list()
        for mv in mvlist:
            x = XMtlZahlung()
            x.mobj_id = mv.mobj_id
            x.mv_id = mv.mv_id
            x.vonMonat, x.bisMonat = getMonthIntervallForCurrentYear( mv.von, mv.bis )
            mzlist.append( x )
        return mzlist

    def _getCondensedEinAusList( self, einausList: List[XEinAus] ) -> List[XEinAus]:
        einausList = sorted( einausList, key=lambda x: x.debi_kredi )

        for ea in einausList:
            for ea2 in einausList:
                if not ea == ea2 \
                        and ea.monat == ea2.monat \
                        and ea.mobj_id == ea2.mobj_id and ea.debi_kredi == ea2.debi_kredi:
                    ea.betrag += ea2.betrag
                    einausList.remove( ea2 )
        return einausList

    def _provideZahlungen( self, mzlist: List[XMtlZahlung], einausList: List[XEinAus] ) -> None:
        """
        Versorgt jedes XMtlZahlung-Objekt in <mzlist> mit den Zahlungsdaten der korrespondierenden
        XEinAus-Objekte aus <einausList>.
        :param mzlist:
        :param einausList:
        :return:
        """
        def getZahlungen( key: str, value: str ) -> List[XEinAus]:
            # key ist "debi_kredi"
            retlist = list()
            for x in einausList:
                if x.__dict__[key] == value:
                    retlist.append( x )
            return retlist

        key = "debi_kredi"
        for mz in mzlist:
            ealist: List[XEinAus] = getZahlungen( key, mz.mv_id )
            for ea in ealist:
                mz.__dict__[ea.monat] += ea.betrag
                mz.summe += ea.betrag

    def _getUniqueMietverhaeltnisse( self, jahr: int ) -> List[XMietverhaeltnisKurz]:
        data = IccData()
        return data.getMietverhaeltnisseKurz( jahr, orderby="mv_id" )


#####################  MtlHausgeldLogic ############################
class MtlHausgeldLogic( MtlEinAusLogic ):
    def __init__( self ):
        MtlEinAusLogic.__init__( self )