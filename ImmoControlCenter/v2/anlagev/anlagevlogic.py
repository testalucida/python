from typing import List

import datehelper
from v2.anlagev.anlagevdata import AnlageVData
from v2.anlagev.anlagevtablemodel import AnlageVTableModel, XAnlageV
from v2.einaus.einausdata import EinAusData
from v2.icc.constants import EinAusArt
from v2.icc.interfaces import XMasterobjekt, XMietobjekt, XEinAus, XSollMiete, XNKAbrechnung
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
        self._sollmieten:List[XSollMiete] = self._smdata.getSollMieten( vj )
        self._sollmieten = sorted( self._sollmieten, key=lambda x: (x.mobj_id, x.von) )
        # for sm in self._sollmieten:
        #     print( sm.mobj_id, ": ", sm.von, " bis ", sm.bis, ": ", sm.netto )
        self._nkalist:List[XNKAbrechnung]

    def getAvailableVeranlagungsjahre( self ) -> List[int]:
        currYear = datehelper.getCurrentYear()
        years = []
        for y in range( currYear-1, 2020, -1 ):
            years.append( y )
        return years

    def getAnlageVTableModels( self ) -> List[AnlageVTableModel]:
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
        mobj_list:List[XMietobjekt] = self._avdata.getMietobjekte( master_name )
        for mobj in mobj_list:
            x.bruttoMiete, x.anzahlMonate = self.getJahresBruttomiete( mobj.mobj_id ) # tatsächlich eingegangene Bruttomiete
            x.nettoMiete, x.nkv = self.getJahresSollNettoUndNkv( mobj.mobj_id ) # wird aus den Soll-Mieten errechnet
            if x.nettoMiete  + x.nkv != x.bruttoMiete:
                msg = "AnlageVLogic.getAnlageVTableModel(), Mietobjekt '%s'\n" \
                      "Brutto-Miete (%d Euro) stimmt nicht mit der Summe " \
                      "aus Netto-Miete (%d Euro) und NKV (%d Euro) überein." \
                      % (mobj.mobj_id, x.bruttoMiete, x.nettoMiete, x.nkv )
                raise Exception( msg )
            x.nka = self.getNka( mobj.mobj_id )

        tm = AnlageVTableModel( x )
        return tm

    def getJahresBruttomiete( self, mobj_id:str ) -> (int, int):
        addWhere = "and mobj_id = '%s'" % mobj_id
        xealist:List[XEinAus] = \
            self._eadata.getEinAusZahlungen( EinAusArt.BRUTTOMIETE.display, self._vj, addWhere )
        monate = len( xealist )
        summe = 0
        for xea in xealist:
            summe += xea.betrag
        return summe, monate

    def getJahresSollNettoUndNkv( self, mobj_id:str ) -> (int, int):
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
        Geliefert wird die Nebenkostenabrechnung des Jahres vor self._vj, denn deren
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


################################################################################
def test():
    log = AnlageVLogic( 2022 )
    tm:AnlageVTableModel = log.getAnlageVTableModel( "RI_Lampennest" )
    print( tm )