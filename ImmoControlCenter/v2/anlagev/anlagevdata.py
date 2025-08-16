from typing import List, Dict

from v2.icc.constants import EinAusArt
from v2.icc.iccdata import IccData
from v2.icc.interfaces import XEinAus, XRueEntn


class AnlageVData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getAfa( self, master_name:str ) -> int:
        sql = "select afa from masterobjekt where master_name = '%s' " % master_name
        tuplelist = self.read( sql )
        return tuplelist[0][0]

    def getEntnahmeRuecklagen( self, master_name, vj:int ) -> int:
        """ Methode liefert nur die Entnahmen, die in <vj> komplett angesetzt werden, also verteilt_auf = 1 """
        sql = "select sum( entnahme_rue ) " \
              "from hg_abrechnung hga " \
              "inner join mietobjekt mo on mo.mobj_id = hga.mobj_id " \
              "where mo.master_name = '%s' " \
              "and hga.ab_jahr = %d and verteilt_auf = 1 " % (master_name, vj)
        tuplelist = self.read( sql )
        if tuplelist and tuplelist[0][0] is not None:
            return int( round( tuplelist[0][0], 0 ) )
        return 0

    def getVerteilteRuecklagenEntnahmen( self, master_name:str ) -> List[XRueEntn]:
        """
        Ermittelt aus Tabelle <hg_abrechnung> alle Sätze für <master_name>, wo hg_abrechnung.entnahme_rue > 0
        und hg_abrechnung.verteilt_auf > 1.
        :param master_name:
        :return: eine Liste von XRueEntn-Objekten
        """
        sql = "select mo.master_name, hga.entnahme_rue as betrag, hga.ab_jahr as jahr, hga.verteilt_auf " \
              "from hg_abrechnung hga " \
              "inner join mietobjekt mo on mo.mobj_id = hga.mobj_id " \
              "where mo.master_name = '%s' " \
              "and verteilt_auf > 1 order by jahr desc " % master_name
        objlist = self.readAllGetObjectList( sql, XRueEntn )
        return objlist

    def getVerteilteAufwaende( self, master_name ) -> List[XEinAus]:
        """
        Ermittelt aus Tabelle <einaus> alle Sätze für master_name, wo ea_art == "rep" und verteilt_auf > 1
        :param master_name:
        :return: eine Liste von XEinAus-Objekten
        """
        ea_art = EinAusArt.REPARATUR.dbvalue
        sql = "select jahr, betrag, verteilt_auf, mobj_id, debi_kredi, leistung, buchungsdatum, buchungstext " \
              "from einaus " \
              "where master_name = '%s' " \
              "and ea_art = '%s' " \
              "and verteilt_auf > 1 " \
              "order by jahr desc" % (master_name, ea_art)
        # dictlist = self.readAllGetDict( sql )
        objlist = self.readAllGetObjectList( sql, XEinAus )
        return objlist

    def getGrundsteuerVersicherungenDivAllg( self, master_name, year:int ) -> Dict:
        """
        Liefert für master_name die Summen der Beträge der EinAusArt'en vers, gs oder allg.
        Geliefert werden also 3 Summen in einem Dict mit den keys vers, gs, allg
        :param master_name:
        :param year: Das Jahr, für das die Zahlungen erfasst wurden
        :return: einen Dictionary, dessen keys den ea_art'en gs, vers, allg entsprechen und dessen values den jeweiligen Summen
                 entsprechen.
        """
        sql = "select ea_art, sum(betrag) as summe " \
              "from einaus " \
              "where master_name = '%s' and jahr = %d " \
              "and ea_art in ('vers', 'gs', 'allg') " \
              "group by ea_art " % (master_name, year)
        tpllist = self.read( sql )
        dic = {}
        for tpl in tpllist:
            dic[tpl[0]] = int( round( tpl[1], 0 ) )
        return dic

    def getReisekosten( self, master_name:str, year:int ) -> int:
        sonst = EinAusArt.SONSTIGE_KOSTEN.dbvalue
        sql = "select sum(betrag) as summe " \
              "from einaus " \
              "where master_name = '%s' and jahr = %d " \
              "and ea_art = '%s' " \
              "and reise_id > 0 " % ( master_name, year, sonst )
        tpllist = self.read( sql )
        reisekosten = 0
        if tpllist and len( tpllist ) > 0 and tpllist[0][0] is not None:
            reisekosten = int( round( tpllist[0][0], 0 ) )
        return reisekosten

    def getSonstigeKostenOhneReisekosten( self, master_name:str, year:int ) -> int:
        sonst = EinAusArt.SONSTIGE_KOSTEN.dbvalue
        sql = "select sum(betrag) as summe " \
              "from einaus " \
              "where master_name = '%s' and jahr = %d " \
              "and ea_art = '%s' " \
              "and (reise_id is NULL or reise_id = 0) " % (master_name, year, sonst)
        tpllist = self.read( sql )
        sonstkosten = 0
        if tpllist and len( tpllist ) > 0 and tpllist[0][0] is not None:
            sonstkosten = int( round( tpllist[0][0], 0 ) )
        return sonstkosten
