from typing import List

from base.databasecommon2 import DatabaseCommon
from interface.interfaces import XDepotPosition
from main.definitions import DATABASE


class InvestMonitorData( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self, DATABASE )

    def getDepotPositions( self ) -> List[XDepotPosition]:
        sql = "select pos.id, isin, ticker, wkn, basic_index, name, gattung, waehrung, flag_acc, beschreibung, " \
              "dep.id as depot_id, dep.bank, dep.nr as depot_nr, dep.vrrkto " \
              "from depotposition pos " \
              "inner join depot dep on dep.id = pos.depot_id " \
              "where flag_displ = 1 "
        xlist = self.readAllGetObjectList( sql, XDepotPosition )
        return xlist


def test():
    data = InvestMonitorData()
    l = data.getDepotPositions()
    print( l )