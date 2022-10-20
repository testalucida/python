from typing import List, Dict

from v2.icc.iccdata import IccData
from v2.icc.interfaces import XSollMiete, XSollHausgeld


class HausgeldData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getSollHausgelder( self, jahr: int ) -> List[XSollHausgeld]:
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr, 12, 31)
        sql = "select shg_id, weg_name, mobj_id, von, bis, netto, ruezufue, bemerkung from sollhausgeld " \
              "where (bis is NULL or bis = '' or bis >= '%s') " \
              "and not von > '%s' " \
              "order by weg_name, von desc" % (minbis, maxvon)
        l:List[XSollHausgeld] = self.readAllGetObjectList( sql, XSollHausgeld )
        for x in l:
            x.brutto = x.netto + x.ruezufue
        return l

##################################################################################

def test():
    data = HausgeldData()
    l = data.getSollHausgelder( 2022 )
    print( l )