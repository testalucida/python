from abc import abstractmethod
from typing import List, Any, Iterable

from PySide2.QtGui import QBrush, Qt

import datehelper
from v2.einaus.einauslogic import EinAusTableModel, EinAusLogic
from v2.icc import constants
from v2.icc.constants import EinAusArt, iccMonthShortNames
from v2.icc.iccdata import IccData
from v2.icc.icclogic import IccSumTableModel, IccTableModel, IccLogic
from v2.icc.interfaces import XMtlZahlung, XEinAus, XMietverhaeltnisKurz, XSollMiete, XMtlMiete, XSollHausgeld, \
    XMtlHausgeld, XMtlAbschlag, XSollAbschlag, XVerwaltung
from v2.mtleinaus.abschlagdata import AbschlagData
from v2.mtleinaus.hausgelddata import HausgeldData
from v2.mtleinaus.mietedata import MieteData


################  MtlEinAusLogic  ############################
from v2.mtleinaus.mtleinaustablemodels import MtlEinAusTableModel, MieteTableModel, HausgeldTableModel, \
    AbschlagTableModel


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
        IccLogic.__init__( self )
        self._ealogic = EinAusLogic()

    @abstractmethod
    def getEinAusArt( self ) -> str:
        pass

    @abstractmethod
    def getDebiKrediKey( self ) -> Any:
        pass


    # @abstractmethod
    # def getMonatsZahlung( debikredi:str, month_sss:str, year:int ) -> XMtlZahlung:
    #     pass

    # def addMonatsZahlung_( self, mobj_id:str, debikredi:str,
    #                       selectedYear:int, selectedMonth:int, value:float, mehrtext:str= "" ) -> XEinAus:
    #     xeinaus = self._ealogic.addZahlung( self.getEinAusArt(), mobj_id, debikredi,
    #                                         selectedYear, selectedMonth, value, mehrtext=mehrtext )
    #     self._ealogic.commit()
    #     return xeinaus

    def addMonatsZahlung( self, x:XMtlZahlung, selectedYear:int, selectedMonth:int,
                          value:float, buchungstext:str= "" ) -> XEinAus:
        debi_kredi = self.getDebiKrediKey()
        xeinaus = self._ealogic.addZahlung( self.getEinAusArt(), x.mobj_id, x.getValue( debi_kredi ),
                                            selectedYear, selectedMonth, value, buchungstext=buchungstext )
        self._ealogic.commit()
        return xeinaus

    def validateMonatsZahlung( self, x:XEinAus ) -> str:
        """
        prüft die Validität der in <x> enthaltenen Daten.
        :param x:
        :return: Leerstring, wenn alles in Ordnung ist, sonst eine Fehlermeldung.
        """
        # todo: master_name, mobj_id, debi_kredi prüfen
        # zunächst nur eine Trivialprüfung:
        if not x.master_name:
            return "Angabe des Masterobjekts fehlt."
        # if not x.mobj_id and not x.ea_art == EinAusArt.REGELM_ABSCHLAG.display:
        if not x.mobj_id and not x.sab_id > 0:  # x.ea_art == EinAusArt.REGELM_ABSCHLAG.display:
            return "Angabe der Wohnung fehlt."
        if not x.debi_kredi:
            return "Angabe von Debitor/Kreditor fehlt."
        if not x.jahr > 2018:
            return "Ungültiges Jahr. Muss größer als 2018 sein."
        if not x.monat in constants.iccMonthShortNames:
            return "Monat ungültig. Muss dreistelliges Monatskürzel wie 'jan' sein."
        if x.betrag == 0:
            return "Betrag ungültig. Muss ungleich 0 sein."
        if not x.ea_art in ( EinAusArt.BRUTTOMIETE.display, EinAusArt.HAUSGELD_VORAUS.display,
                             EinAusArt.KOMMUNALE_DIENSTE.display ):
            return "Ungültige EinAusArt. Muss BRUTTOMIETE, HAUSGELD_VORAUS oder KOMMUNALE_DIENSTE sein."
        return ""

    def updateMonatsZahlung( self, x:XEinAus ):
        msg = self.validateMonatsZahlung( x )
        if msg:
            raise Exception( "MtlEinAusLogic.updateMonatsZahlung():\nValidierung fehlerhaft:\n%s" % msg )
        self._ealogic.updateZahlung( x )
        self._ealogic.commit()

    def getZahlungenModelObjektMonat( self, mobj_id, year:int, monthIdx:int ) -> EinAusTableModel:
        ea_art_display = self.getEinAusArt()
        return self._ealogic.getZahlungenModel2( ea_art_display, year, monthIdx, mobj_id )

    def getZahlungenModelDebiKrediMonat( self, debikredi:str, year:int, monthIdx:int ) -> EinAusTableModel:
        """
        Liefert für einen DebiKredi alle Zahlungen für einen Monat.
        :param debikredi: ein Mieter oder eine WEG oder ein Versorger, der monatliche Abschläge erhebt.
        :param year:
        :param monthIdx:
        :return:
        """
        ea_art_display = self.getEinAusArt()
        return self._ealogic.getZahlungenModel3( ea_art_display, year, monthIdx, debikredi )

    def deleteZahlungen( self, ealist:List[XEinAus], model:MtlEinAusTableModel ):
        """
        Die XEinAus-Objekte aus <xlist> werden aus der Datenbank, Tabelle <einaus> gelöscht.
        Aus <model> müssen dann die XMtlZahlung-Objekte entfernt, neu berechnet und wieder eingefügt werden,
        die von der Löschung der Einzelzahlungen betroffen sind.
        Die XMtlZahlung-Objekte werden anhand debi_kredi, jahr und monat gefunden.
        :param xlist:
        :param model:
        :return:
        """
        self._ealogic.deleteZahlungen( ealist )
        self._ealogic.commit()
        # wir sind noch hier, also hat die DB-Löschung der Einzelzahlungen funktioniert.
        # aus dem Model die betroffenen XMTlZahlung-Objekte finden
        mtlZlist:List[XMtlZahlung] = model.getRowList()
        debikredikey = self.getDebiKrediKey()
        for ea in ealist: # ea: eine einzelne Zahlung, die gerade aus der Tabelle einaus gelöscht wurde
            for mtlZ in mtlZlist: # mtlZ: Monatszahlung ggf. bestehend aus mehreren Einzelzahlungen
                if mtlZ.getValue( debikredikey ) == ea.debi_kredi:
                    mtlZ.__dict__[ea.monat] -= ea.betrag
                    model.objectUpdatedExternally( mtlZ )
                    # model.removeObject( mtlZ )
                    # mtlZneu = self.getMonatsZahlung( mtlZ.getValue( debikredikey ), ea.monat, ea.jahr )

    def getMonthIntervallForCurrentYear( self, jahr:int, isoVon: str, isoBis: str ) -> (str, str):
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
        jahrStart = str( jahr ) + "-01-01"
        jahrEnd = str( jahr ) + "-12-31"
        if datehelper.isWithin( isoVon, jahrStart, jahrEnd ):
            firstMon = iccMonthShortNames[vonM - 1]
        else:
            firstMon = iccMonthShortNames[0]
        if datehelper.isWithin( isoBis, jahrStart, jahrEnd ):
            lastMon = iccMonthShortNames[bisM - 1]
        else:
            lastMon = iccMonthShortNames[11]
        return firstMon, lastMon

    def getCondensedEinAusList( self, einausList: List[XEinAus] ) -> List[XEinAus]:
        """
        Verdichtet die übergebene <einausList> auf debi_kredi, d.h., alle Beträge in den in <einausList> enthaltenen
        XEinAus-Objekten, die sich auf den gleichen debi_kredi beziehen, werden auf *ein* XeinAus-Objekt addiert;
        die anderen XEinAus-Objekte des gleichen debi_kredi werden gelöscht.
        So erhält man je debi_kredi und monat (und mobj_id) ein einziges XEinAus-Objekt.
        :param einausList: Liste mit den zu verdichtenden XEinAus-Objekten.
        :return: die verdichtete, *also geänderte* einausList
        """
        einausList = sorted( einausList, key=lambda x: x.debi_kredi )
        for ea in einausList:
            for ea2 in einausList:
                if not ea == ea2 \
                        and ea.monat == ea2.monat \
                        and ea.master_name == ea2.master_name \
                        and ea.mobj_id == ea2.mobj_id  \
                        and ea.debi_kredi == ea2.debi_kredi:
                    ea.betrag += ea2.betrag
                    einausList.remove( ea2 )
        return einausList

    @abstractmethod
    def selectedMonthChanged( self, model:MtlEinAusTableModel, newMonthIdx:int ):
        """
        im Model müssen neue Sollwerte angelegt werden.
        :param model:
        :param newMonthIdx:
        :return:
        """


#####################  MieteLogic SINGLETON  ############################
class MieteLogic( MtlEinAusLogic ):
    #__instance = None
    def __init__( self ):
        MtlEinAusLogic.__init__( self ) # call to super class
        self._mieteData = MieteData()
        #MieteLogic.__instance = self

    def getEinAusArt( self ) -> str:
        return EinAusArt.BRUTTOMIETE.display

    def getDebiKrediKey( self ) -> Any:
        return "mv_id"

    # def getMonatsZahlung( debikredi:str, month_sss:str, year:int ) -> XMtlZahlung:
    #     #todo

    def createMietzahlungenModel( self, jahr: int, checkmonatIdx:int=None ) -> MieteTableModel:
        l:List[XMtlMiete] = self.getMietzahlungen( jahr, checkmonatIdx )
        tm = MieteTableModel( l, jahr, checkmonatIdx )
        return tm

    def getMietzahlungen( self, jahr: int, checkmonatIdx:int=None ) -> List[XMtlMiete]:
        """
        Liefert eine Liste aller gezahlten Monatsmieten im Monat <checkmonat> aller Mieter in <jahr>
        Hat ein Mieter in einem Monat mehrere Teilbeträge bezahlt, werden diese in 1 XMtlZahlung-Objekt verdichtet.
        :param jahr: Jahr, für das die Mietzahlungen zu ermitteln sind
        :param checkmonatIdx: Der Index des Monats - BEGINNEND BEI 0 -,
        der zur Bearbeitung ausgewählt ist. Für diesen Monat werden die Sollmieten in
                         der UI-Tabelle angezeigt.
        :return:
        """
        einausList: List[XEinAus] = self._ealogic.getZahlungen( EinAusArt.BRUTTOMIETE.display, jahr )
        # Annahme: in einausList können mehrere Zahlungsvorgänge eines Debitors/Kreditors sein, die den gleichen Monat
        # betreffen.
        # Deshalb muss die einausList zunächst auf Monate verdichtet werden,
        # und vor dem Verdichten wird sie nach Mietern (Debitoren) sortiert.
        einausList = self.getCondensedEinAusList( einausList )
        # einausList enthält nun je Mieter (Debitor) und Monat ein XEinAus-Objekt und ist nach Mietern sortiert.
        # Nicht für jeden Monat muss ein XEinAus-Objekt vorhanden sein.

        # Die Liste der XEinAus-Objekte muss nun in eine Liste von XMtlZahlung-Objekte umgewandelt werden (für das
        # TableModel).
        # Dafür müssen wir zuerst eine Liste der in <jahr> aktiven Mietverhältnisse holen:
        mvlist: List[XMietverhaeltnisKurz] = self._getUniqueMietverhaeltnisse( jahr )
        # je XMietverhaeltnisKurz-Objekt in mvlist ein XMtlZahlung-OBjekt anlegen und in die XMtlZahlung-Liste packen:
        mietelist:List[XMtlMiete] = self._convertMietVhToMtlZahlg( mvlist, jahr )
        # die XMtlZahlung-Objekte in mzlist müssen jetzt noch mit den Zahlungsdaten versorgt werden:
        self._provideZahlungen( mietelist, einausList )
        #self.provideSollMieten( jahr, constants.iccMonthShortNames[checkmonatIdx], mietelist )
        self.provideSollMieten( jahr, checkmonatIdx, mietelist )
        return mietelist

    #def provideSollMieten( self, jahr:int, monat:str, mzlist:List[XMtlMiete] ) -> List[XMtlMiete]:
    def provideSollMieten( self, jahr: int, monatIdx:int, mzlist: List[XMtlMiete] ) -> List[XMtlMiete]:
        """
        Arbeitet in <mzlist> die Monats-Sollwerte des Monats <jahr>/<monat> ein.
        Wird benötigt, wenn im UI der Monat umgestellt wird.
        Jedes XMtlZahlung-Objekt entspricht einer Zeile in der UI-Tabelle.
        :param jahr:
        :param monat: gem. iccMonthShortNames
        :param mzlist: die Liste mit XMtlZahlung-Objekten, die mit den Sollwerten für <jahr>/<monat> aktualisiert werden soll
        :return: die aktualisierte <mzlist>
        """
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

    def _convertMietVhToMtlZahlg( self, mvlist: List[XMietverhaeltnisKurz], jahr: int ) -> List[XMtlMiete]:
        mietelist: List[XMtlMiete] = list()
        for mv in mvlist:
            x = XMtlMiete()
            x.mobj_id = mv.mobj_id
            x.mv_id = mv.mv_id
            x.vonMonat, x.bisMonat = self.getMonthIntervallForCurrentYear( jahr, mv.von, mv.bis )
            mietelist.append( x )
        return mietelist

    def _provideZahlungen( self, mzlist: List[XMtlMiete], einausList: List[XEinAus] ) -> None:
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

    def selectedMonthChanged( self, model: MieteTableModel, newMonthIdx: int ):
        # todo
        sollmieteListe:List[XSollMiete] = self.getSollMieten( model.getJahr(), newMonthIdx )
        rowlist:List[XMtlMiete] = model.rowList
        for mtlmiete in rowlist:
            found = False
            for sm in sollmieteListe:
                if sm.mv_id == mtlmiete.mv_id:
                    mtlmiete.soll = sm.brutto
                    found = True
                    break
            if not found:
                mtlmiete.soll = 0




#####################  HausgeldLogic ############################
class HausgeldLogic( MtlEinAusLogic ):
    def __init__( self ):
        MtlEinAusLogic.__init__( self )
        self._hausgeldData = HausgeldData()

    # def createHausgeldzahlungenModel( self, jahr: int, checkmonatIdx:int=None ) -> HausgeldTableModel:
    #     zlist:List[XEinAus] = self._ealogic.getZahlungen( EinAusArt.HAUSGELD_VORAUS, jahr )
    #     zlist = self.getCondensedEinAusList( zlist )
    #     # die XEinAus-Liste in XMtlHausgeld-Liste umwandeln:
    #     xhglist:List[XMtlHausgeld] = list()
    #     memo = ""
    #     xhg:XMtlHausgeld = None
    #     for xea in zlist:
    #         if xea.debi_kredi != memo:
    #             xhg = XMtlHausgeld()
    #             xhg.weg_name = xea.debi_kredi
    #             xhg.mobj_id = xea.mobj_id
    #             self._provideVonBis( jahr, xhg )
    #             xhglist.append( xhg )
    #             memo = xea.debi_kredi
    #         xhg.__dict__[xea.monat] = xea.betrag
    #         xhg.computeSum()
    #     self._provideSollHausgelder( jahr, checkmonatIdx, xhglist )
    #     tm = HausgeldTableModel( xhglist, jahr, checkmonatIdx )
    #     return tm

    def createHausgeldzahlungenModel( self, jahr: int, checkmonatIdx:int=None ) -> HausgeldTableModel:
        vwlist:List[XVerwaltung] = self._hausgeldData.getVerwaltungen( jahr )
        zlist:List[XEinAus] = self._ealogic.getZahlungen( EinAusArt.HAUSGELD_VORAUS.display, jahr )
        zlist = self.getCondensedEinAusList( zlist )
        # die XEinAus-Liste in XMtlHausgeld-Liste umwandeln:
        xhglist:List[XMtlHausgeld] = list()
        for vw in vwlist:
            # für jede Verwaltung ein XMtlHausgeld-Objekt anlegen
            xhg = XMtlHausgeld() # ein XMtlHausgel-OBjekt entspricht einer Zeile in der Tabelle
            xhg.master_name = vw.master_name
            xhg.mobj_id = vw.mobj_id
            xhg.weg_name = vw.weg_name #+ " (" + vw.vw_id + ") "
            self._provideVonBis( jahr, xhg, vw )
            for xea in zlist:
                # die Monatsbeträge aus den XEinAus-Objekten in das XMtlHausgeld-Objekt übertragen
                if xea.debi_kredi == xhg.weg_name:
                    xhg.__dict__[xea.monat] = xea.betrag
                    xhg.computeSum()
            xhglist.append( xhg )
        self._provideSollHausgelder( jahr, checkmonatIdx, xhglist )
        tm = HausgeldTableModel( xhglist, jahr, checkmonatIdx )
        return tm

    def _provideVonBis( self, jahr, xhg:XMtlHausgeld, vw:XVerwaltung ):
        """
        Versorgt die Attribute xhg.vonMonat und xhg.bisMonat mit dem im Jahr <jahr> aktiven Monatsintervall.
        Basis sind die Datümer vw.von und vw.bis
        :param xhg:
        :return:
        """
        # anschaffungsdatum, verkaufsdatum = self._hausgeldData.getAnschaffungsUndVerkaufsdatum2( xhg.master_name )
        xhg.vonMonat, xhg.bisMonat =  self.getMonthIntervallForCurrentYear( jahr, vw.von, vw.bis )

    def _provideSollHausgelder( self, jahr:int, monatIdx:int, xhglist:List[XMtlHausgeld] ) -> List[XMtlHausgeld]:
        sollHgList = self.getSollHausgelder( jahr, monatIdx )
        for hg in xhglist:
            for soll in sollHgList:
                if soll.weg_name == hg.weg_name and soll.mobj_id == hg.mobj_id:
                    hg.soll = soll.brutto
                    break
        return xhglist

    def getSollHausgelder( self, jahr: int, monatIdx:int ) -> List[XSollHausgeld]:
        """
        Liefert alle Soll-Hausgelder, die im Jahr <jahr> und Monat <monat> gültig waren.
        Annahme: Hausgelder ändern sich ausschließlich zum 1. eines Moants
        :param jahr:
        :param monatIdx: Monatsindex. Januar = 0, Dezember = 11
        :return:
        """
        check = "%d-%02d-%02d" % (jahr, monatIdx+1, 1)
        l:List[XSollHausgeld] = self._hausgeldData.getSollHausgelder( jahr )
        retlist:List[XSollHausgeld] = list()
        for x in l:
            if datehelper.isWithin( check, x.von, x.bis ):
                retlist.append( x )
        return retlist

    def getEinAusArt( self ) -> str:
        return EinAusArt.HAUSGELD_VORAUS.display

    def getDebiKrediKey( self ) -> Any:
        return "weg_name"

    def selectedMonthChanged( self, model: MtlEinAusTableModel, newMonthIdx: int ):
        # todo
        pass

#####################  AbschlagLogic ############################
class AbschlagLogic( MtlEinAusLogic ):
    def __init__( self ):
        MtlEinAusLogic.__init__( self )
        self._abschlagData = AbschlagData()

    def createAbschlagzahlungenModel( self, jahr: int, checkmonatIdx:int=None ) -> AbschlagTableModel:
        #zlist:List[XEinAus] = self._ealogic.getZahlungen( EinAusArt.REGELM_ABSCHLAG.display, jahr )
        zlist_allg: List[XEinAus] = self._ealogic.getZahlungen( EinAusArt.ALLGEMEINE_KOSTEN.display, jahr )
        zlist_sonst: List[XEinAus] = self._ealogic.getZahlungen( EinAusArt.SONSTIGE_KOSTEN.display, jahr )
        zlist = zlist_allg + zlist_sonst
        zlist = self._getCondensedEinAusList( zlist ) # zlist enthält für jede sab_id und jeden Monat genau 1 XEinAus-Objekt
        sollAbschlagList:List[XSollAbschlag] = self._abschlagData.getSollabschlaege( jahr )
        # die XEinAus-Liste in XMtlAbschlag-Liste umwandeln:
        xablist:List[XMtlAbschlag] = list()
        for sollabschlag in sollAbschlagList:
            # aus jedem sollabschlag ein XMtlAbschlag-Objekt machen:
            xab = XMtlAbschlag()
            xab.sab_id = sollabschlag.sab_id
            xab.ea_art = sollabschlag.ea_art
            xab.master_name = sollabschlag.master_name
            xab.mobj_id = sollabschlag.mobj_id
            xab.kreditor = sollabschlag.kreditor
            self._completeData( xab, xab.sab_id, jahr, checkmonatIdx+1, sollAbschlagList )
            # dem XMtlAbschlag-Objekt die einzelnen Zahlungen zuordnen
            for xea in zlist:
                if xea.sab_id == xab.sab_id:
                   xab.__dict__[xea.monat] = xea.betrag
            xab.computeSum()
            xablist.append( xab )
        tm = AbschlagTableModel( xablist, jahr, checkmonatIdx )
        return tm

    def _getCondensedEinAusList( self, einausList: List[XEinAus] ) -> List[XEinAus]:
        """
        Verdichtet die übergebene <einausList> auf sab_id, d.h., alle Beträge in den in <einausList> enthaltenen
        XEinAus-Objekten, die sich auf die gleichen sab_id beziehen, werden auf *ein* XeinAus-Objekt addiert;
        die anderen XEinAus-Objekte der gleichen sab_id werden gelöscht.
        So erhält man je sab_id und monat ein einziges XEinAus-Objekt.
        :param einausList: Liste mit den zu verdichtenden XEinAus-Objekten.
        :return: die verdichtete, *also geänderte* einausList
        """
        einausList = sorted( einausList, key=lambda x: x.sab_id )
        for ea in einausList:
            for ea2 in einausList:
                if not ea == ea2 \
                        and ea.monat == ea2.monat \
                        and ea.sab_id == ea2.sab_id:
                    ea.betrag += ea2.betrag
                    einausList.remove( ea2 )
        return einausList


    def _completeData( self, xab:XMtlAbschlag, sab_id:int,
                       jahr:int, monat:int, sollAbschlagList:List[XSollAbschlag] ) -> None:
        """
        Ergänzt die Daten Sollbetrag, Leistung und Vertragsnummer im Objekt <xab>, indem es das für <jahr> und <monat>
        passende XSollAbschlag aus <sollAbschlagList> heraussucht und dessen Daten überträgt.
        :param xab:  das zu ergänzende XMtlAbschlag-Objekt
        :param sab_id: die ID des Soll-Abschlags
        :param jahr:
        :param monat: Januar = 1, ...
        :param abschlagList: die Liste aller XSollAbschlag-Objekte des Jahres <jahr>
        :return:
        """
        def isCheckdateWithin( sollvon:str, sollbis:str ) -> bool:
            #print( checkdate, ", ", sollvon )
            sollbis = "9999-12-31" if not sollbis else sollbis
            return datehelper.isWithin( checkdate, sollvon, sollbis )

        checkdate = str( jahr ) + "-" + ("%2d" % monat) + "-" + "01"
        for xsa in sollAbschlagList:
            if xsa.sab_id == sab_id and isCheckdateWithin( xsa.von, xsa.bis ):
                xab.soll = xsa.betrag
                xab.vnr = xsa.vnr
                xab.leistung = xsa.leistung
                xab.vonMonat, xab.bisMonat = self.getMonthIntervallForCurrentYear( jahr, xsa.von, xsa.bis )
                return
        raise Exception( "AbschlagLogic._completeData():\n"
                         "Sollabschlag nicht gefunden: "
                         "sab_id = %d, jahr = %d, monat = %d " % ( sab_id, jahr, monat ) )

    def addMonatsZahlung( self, x:XMtlAbschlag, selectedYear:int, selectedMonth:int,
                          value:float, mehrtext:str= "" ) -> XEinAus:
        dic = self._abschlagData.getVnrUndEaArtUndUmlegbar( x.sab_id )
        x.leistung += (" (%s)" % dic["vnr"])
        x.ea_art = EinAusArt.getDisplay( dic["ea_art"] )
        xeinaus = self._ealogic.addZahlung2( x.ea_art, x.master_name, x.mobj_id, x.kreditor,
                                             x.sab_id, x.leistung,
                                             selectedYear, selectedMonth, value, dic["umlegbar"] )
        self._ealogic.commit()
        return xeinaus

    def getEinAusArt( self ) -> str:
        raise Exception( "AbschlagLogic.getEinAusArt()\nDiese Methode ist nicht aufrufbar,\nda sie kein "
                         "eindeutiges Ergebnis liefern kann.\nDie EinAusArt kann 'allg' oder 'sonst' sein." )

    def getDebiKrediKey( self ) -> Any:
        return "kreditor"

    def getEinzelzahlungenModel( self, sab_id:int, year:int, monthIdx:int ) -> EinAusTableModel:
        eatm:EinAusTableModel = self._ealogic.getZahlungenModel4( sab_id, year, monthIdx )
        keys = ("master_name", "mobj_id", "debi_kredi", "sab_id", "jahr", "monat", "betrag", "write_time")
        headers = ("Haus", "Wohnung", "Firma", "sab_id", "Jahr", "Monat", "Betrag", "gebucht am")
        eatm.setKeyHeaderMappings2( keys, headers )
        return eatm

    def selectedMonthChanged( self, model: MtlEinAusTableModel, newMonthIdx: int ):
        # todo
        pass


def test():
    logic = AbschlagLogic()
    tm = logic.createAbschlagzahlungenModel( 2022, 10 )
    print( tm )