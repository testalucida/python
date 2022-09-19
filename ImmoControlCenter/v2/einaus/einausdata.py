from typing import List, Dict

from v2.icc.constants import EinAusArt
from v2.icc.iccdata import IccData
from v2.icc.interfaces import XEinAus


class EinAusData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getEinAusZahlungen( self, ea_art: EinAusArt, jahr: int ) -> List[XEinAus]:
        sql = "select ea_id, master_name, mobj_id, debitor, kreditor, jahr, monat, betrag, ea_art, verteilt_auf, " \
              "umlegbar, buchungsdatum, buchungstext, mehrtext " \
              "from einaus " \
              "where jahr = %d " \
              "and ea_art = '%s' " % (jahr, ea_art.value[0])
        xlist = self.readAllGetObjectList( sql, XEinAus )
        return xlist

    def getJahre( self ) -> List[int]:
        """
        Liefert die Jahreszahlen, zu denen Daten in der Tabelle einaus erfasst sind.
        :return:
        """
        sql = "select distinct jahr " \
              "from einaus " \
              "order by jahr desc "
        l:List[Dict] = self.readAllGetDict( sql )
        return [d["jahr"] for d in l]

######################################################################
def test():
    ea_art = EinAusArt.BRUTTOMIETE
    print( ea_art.value[0] )

    data = EinAusData()
    l = data.getJahre()
    print( l )
    l = data.getEinAusZahlungen( EinAusArt.BRUTTOMIETE, 2022 )
    print( l )