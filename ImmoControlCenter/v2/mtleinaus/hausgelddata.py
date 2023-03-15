from typing import List, Dict

from v2.icc.iccdata import IccData
from v2.icc.interfaces import XSollMiete, XSollHausgeld, XVerwaltung


class HausgeldData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getSollHausgelder( self, jahr: int ) -> List[XSollHausgeld]:
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr, 12, 31)
        sql = "select shg.shg_id, shg.vwg_id, vwg.weg_name, vwg.master_name, shg.von, shg.bis, " \
              "shg.netto, shg.ruezufue, shg.bemerkung " \
              "from sollhausgeld shg " \
              "inner join verwaltung vwg on vwg.vwg_id = shg.vwg_id " \
              "where (shg.bis is NULL or shg.bis = '' or shg.bis >= '%s') " \
              "and not shg.von > '%s' " \
              "order by vwg.weg_name, shg.von desc" % (minbis, maxvon)
        l:List[XSollHausgeld] = self.readAllGetObjectList( sql, XSollHausgeld )
        for x in l:
            x.brutto = x.netto + x.ruezufue
        return l

##################################################################################

def test():
    data = HausgeldData()
    l = data.getSollHausgelder( 2022 )
    print( l )