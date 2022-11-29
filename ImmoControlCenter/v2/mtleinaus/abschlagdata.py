from typing import List, Dict

from v2.icc.iccdata import IccData
from v2.icc.interfaces import XSollMiete, XSollAbschlag


class AbschlagData( IccData ):
    def __init__(self):
        IccData.__init__( self )

    def getSollabschlaege( self, jahr: int ) -> List[XSollAbschlag]:
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr, 12, 31)
        sql = "select sab_id, kreditor, vnr, leistung, master_name, coalesce(mobj_id, '') as mobj_id, " \
              "von, coalesce(bis, '') as bis, " \
              "betrag, umlegbar, coalesce(bemerkung, '') as bemerkung " \
              "from sollabschlag " \
              "where (bis is NULL or bis = '' or bis >= '%s') " \
              "and not von > '%s' " \
              "order by kreditor, mobj_id, von desc" % (minbis, maxvon)
        l:List[XSollAbschlag] = self.readAllGetObjectList( sql, XSollAbschlag )
        return l

    def getUmlegbar( self, sab_id:int ) -> str:
        sql = "select umlegbar from sollabschlag where sab_id = " + str( sab_id )
        dic = self.readOneGetDict( sql )
        return dic["umlegbar"]


##################################################################################

def test():
    data = AbschlagData()
    l = data.getSollabschlaege( 2022 )
    print( l )
    u = data.getUmlegbar( 2 )
    print( u )