from typing import List, Dict

import datehelper
from v2.anlagev.anlagevdata import AnlageVData
from v2.anlagev.anlagevtablemodel import AnlageVTableModel, XAnlageV
from v2.einaus.einausdata import EinAusData
from v2.icc.constants import EinAusArt
from v2.icc.interfaces import XMasterobjekt, XMietobjekt, XEinAus, XSollMiete, XNKAbrechnung, XSollHausgeld
from v2.sollhausgeld.sollhausgelddata import SollHausgeldData
from v2.sollmiete.sollmietedata import SollmieteData


class AnlageVLogic:
    def __init__(self, vj:int ):
        """
        :param vj: das Veranlagungsjahr, um das es sich in allen Methoden dieser Instanz dreht.
        """
        self._vj = vj
        self._avdata = AnlageVData()
        self._eadata = EinAusData()
        self._smdata = SollmieteData()
        self._shgdata = SollHausgeldData()
        self._sollmieten:List[XSollMiete] = self._smdata.getSollMieten( vj )
        self._sollmieten = sorted( self._sollmieten, key=lambda x: (x.mobj_id, x.von) )
        self._sollhausgelder: List[XSollHausgeld] = self._shgdata.getSollHausgelder( vj )
        self._sollhausgelder = sorted( self._sollhausgelder, key=lambda x: (x.mobj_id, x.von) )

    @staticmethod
    def getAvailableVeranlagungsjahre() -> List[int]:
        currYear = datehelper.getCurrentYear()
        years = []
        for y in range( currYear-1, 2020, -1 ):
            years.append( y )
        return years

    @staticmethod
    def getDefaultVeranlagungsjahr() -> int:
        currYear = datehelper.getCurrentYear()
        return currYear - 1

    def getAnlageVTableModels( self ) -> List[AnlageVTableModel]:
        """
        Liefert eine Liste von AnlageVTableModels.
        Für jedes Masterobjekt ist ein AnlageVTableModel in der Liste enthalten.
        :return:
        """
        masterobjects = self._avdata.getMasterobjekte()
        l = list()
        for master in masterobjects:
            tm = self.getAnlageVTableModel( master.master_name )
            l.append( tm )
        return l

    def getAnlageVTableModel( self, master_name:str ) -> AnlageVTableModel:
        """
        Liefert das AnlageVTableModel für alle Mietobjekte eines MasterObjekts
        :param master_name:
        :return:
        """
        x = XAnlageV()
        x.vj = self._vj
        x.master_name = master_name

        # Aufwände, die für das ganze steuerliche Objekt (master_objekt, repr.durch master_name) ermittelt werden
        x.afa = self._avdata.getAfa( master_name )
        # Erhalt.-Aufwände, die sofort und voll abgesetzt werden:
        xealist = self._eadata.getEinAusZahlungen( EinAusArt.REPARATUR.display, self._vj,
                                                   "and master_name = '%s' and verteilt_auf = 1 " % master_name )
        x.erhaltg_voll = int( round( sum( [xea.betrag for xea in xealist] ), 0 ) )
        x.entnahme_rue = self._avdata.getEntnahmeRuecklagen( master_name, self._vj )
        # zu verteilende Erhaltungsaufwände:
        self.provideVerteilteAufwaende( master_name, x )
        x.reisekosten = self._avdata.getReisekosten( master_name, self._vj )
        x.sonstige = self._avdata.getSonstigeKostenOhneReisekosten( master_name, self._vj )

        # Aufwände, die für die einzelne Wohnung ermittelt (und auf den master aufsummiert) werden müssen
        mobj_list:List[XMietobjekt] = self._avdata.getMietobjekte( master_name )
        for mobj in mobj_list:
            #########  Einnahmen  ############
            bruttoMiete, anzahlMonate = self.getJahresBruttomiete( mobj.mobj_id ) # tatsächlich eingegangene Bruttomiete
            x.bruttoMiete += bruttoMiete
            x.anzahlMonate += anzahlMonate
            nettoMiete, nkv = self.getJahresSollNettoMieteUndNkv( mobj.mobj_id ) # wird aus den Soll-Mieten errechnet
            x.nettoMiete += nettoMiete
            x.nkv += nkv
            nka = self.getNka( mobj.mobj_id )
            x.nka += nka
            #########  Ausgaben  ############
            hgv_netto = self.getJahresSollNettoHausgeld( mobj.mobj_id )
            x.hgv_netto += hgv_netto
            hga = self.getHga( mobj.mobj_id )
            x.hga += hga
        tm = AnlageVTableModel( x )
        return tm

    def provideVerteilteAufwaende( self, master_name:str, xav:XAnlageV ):
        """
        # Versorgt xav mit *allen* zu verteilenden Aufwände.
        # Das sind sowohl die, die aus Vj stammen, als auch die, die aus den Vj-Vorjahren kommen.
        :param master_name:
        :param xav:
        :return:
        """
        vertAufwDictList: List[Dict] = self._avdata.getVerteilteAufwaende( master_name )
        # Achtung:
        # da sind auch Aufwände dabei,
        #    - die aus einem Jahr > Vj stammen, die erst nächstes Vj berücksichtigt werden dürfen
        #    - die aus einem ganz alten Jahr stammen, die nicht mehr berücksichtigt werden dürfen
        gesamtaufwand_in_vj = 0
        for aufw in vertAufwDictList:
            aufwJahr = aufw["jahr"]
            aufwBetrag = aufw["betrag"]
            aufwVerteiltAuf = aufw["verteilt_auf"]
            aufwAnteilig = int(round(aufwBetrag/aufwVerteiltAuf, 0))
            diff = self._vj - aufwJahr
            if diff < 0:
                # Aufwand in einem Vj-Folgejahr, irrelevant
                continue
            if diff == 0:
                # dieser Aufwand wurde im Vj erbracht. Er ist als (Teil vom) Gesamtaufwand auszuweisen
                # und anteilig im Feld "davon im Vj abzuziehen"
                xav.verteil_aufwand_im_vj_angefallen += aufwBetrag
                xav.erhaltg_anteil_vj += aufwAnteilig
            elif diff == 1:
                xav.erhaltg_anteil_vjminus1 += aufwAnteilig
            elif diff == 2:
                xav.erhaltg_anteil_vjminus2 += aufwAnteilig
            elif diff == 3:
                xav.erhaltg_anteil_vjminus3 += aufwAnteilig
            elif diff == 4:
                xav.erhaltg_anteil_vjminus4 += aufwAnteilig
            self.provideAllgemeineHauskosten( master_name, xav )

    def provideAllgemeineHauskosten( self, master_name:str, xav:XAnlageV ):
        dic = self._avdata.getGrundsteuerVersicherungenDivAllg( master_name, self._vj )
        xav.grundsteuer = dic.get( EinAusArt.GRUNDSTEUER.dbvalue, 0 )
        xav.versicherungen = dic.get( EinAusArt.VERSICHERUNG.dbvalue, 0 )
        xav.divAllgHk = dic.get( EinAusArt.ALLGEMEINE_KOSTEN.dbvalue, 0 )

    def getJahresBruttomiete( self, mobj_id:str ) -> (int, int):
        addWhere = "and mobj_id = '%s'" % mobj_id
        xealist:List[XEinAus] = \
            self._eadata.getEinAusZahlungen( EinAusArt.BRUTTOMIETE.display, self._vj, addWhere )
        monate = len( xealist )
        summe = 0
        for xea in xealist:
            summe += xea.betrag
        return summe, monate

    def getJahresSollNettoMieteUndNkv( self, mobj_id:str ) -> (int, int):
        smlist:List[XSollMiete] = [sm for sm in self._sollmieten if sm.mobj_id == mobj_id]
        summeNetto = 0
        summeNkv = 0
        for sm in smlist:
            months = datehelper.getNumberOfMonths( sm.von, sm.bis, self._vj )
            summeNetto += months * sm.netto
            summeNkv += months * sm.nkv
        return summeNetto, summeNkv

    def getNka( self, mobj_id:str ) -> int:
        """
        Geliefert wird das Ergebnis der Nebenkostenabrechnung des Jahres vor self._vj, denn deren
        Ergebnis wurde in self._vj entrichtet.
        :param mobj_id:
        :return:
        """
        year = self._vj - 1
        nkaList:List[XEinAus] = \
            self._eadata.getEinAusZahlungen( EinAusArt.NEBENKOSTEN_ABRECHNG.display, year, "and mobj_id = '%s' "
            % mobj_id )
        nka = sum([xea.betrag for xea in nkaList])
        return nka

    def getJahresSollNettoHausgeld( self, mobj_id: str ) -> int:
        """
        Liefert die Summe des Netto-Hausgelds (ohne RüZuFü), das im Veranlagungsjahr gem. Soll-Hausgeld hätte
        entrichtet werden sollen.
        :param mobj_id:
        :return:
        """
        shgvlist:List[XSollHausgeld] = [shgv for shgv in self._sollhausgelder if shgv.mobj_id == mobj_id]
        summeNetto = 0
        for shgv in shgvlist:
            months = datehelper.getNumberOfMonths( shgv.von, shgv.bis, self._vj )
            summeNetto += months * shgv.netto
        return summeNetto

    def getHga( self, mobj_id:str ) -> int:
        """
        Geliefert wird das Ergebnis der Hausgeldabrechnung des Jahres vor self._vj, denn deren
        Ergebnis wurde in self._vj entrichtet.
        :param mobj_id:
        :return:
        """
        year = self._vj - 1
        hgaList:List[XEinAus] = \
            self._eadata.getEinAusZahlungen( EinAusArt.HAUSGELD_ABRECHNG.display, year, "and mobj_id = '%s' "
            % mobj_id )
        hga = sum([xea.betrag for xea in hgaList])
        return hga

################################################################################
def test():
    log = AnlageVLogic( 2022 )
    tm:AnlageVTableModel = log.getAnlageVTableModel( "RI_Lampennest" )
    print( tm )