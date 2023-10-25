from typing import List

from base.databasecommon2 import DatabaseCommon
from interface.interfaces import XDepotPosition, XDelta
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

    def getAllMyTickers( self ) -> List[str]:
        sql = "select ticker " \
              "from depotposition pos " \
              "where flag_displ = 1 "
        tupleList = self.read( sql )
        tickerlist = [tpl[0] for tpl in tupleList]
        return tickerlist

    def getDeltas( self, ticker:str ) -> List[XDelta]:
        sql = "select id, ticker, delta_stck, delta_datum, preis_stck, bemerkung " \
              "from delta " \
              "where ticker = '%s' " % ticker
        xlist = self.readAllGetObjectList( sql, XDelta )
        return xlist




def test():
    data = InvestMonitorData()
    #l = data.getDepotPositions()
    strlist = data.getAllMyTickers()
    print( strlist )
    deltalist = data.getDeltas( "WTEM.DE" )
    print( deltalist )
