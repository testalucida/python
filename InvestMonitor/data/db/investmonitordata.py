from typing import List

from base.databasecommon2 import DatabaseCommon
from interface.interfaces import XDepotPosition, XDelta
from imon.definitions import DATABASE


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

    def getDepotPosition( self, ticker:str ) -> XDepotPosition:
        sql = "select pos.id, isin, ticker, wkn, basic_index, name, gattung, waehrung, flag_acc, beschreibung, " \
              "dep.id as depot_id, dep.bank, dep.nr as depot_nr, dep.vrrkto " \
              "from depotposition pos " \
              "inner join depot dep on dep.id = pos.depot_id " \
              "where ticker = '%s' " % ticker
        x = self.readOneGetObject( sql, XDepotPosition )
        return x

    def getDeltas( self, wkn:str ) -> List[XDelta]:
        sql = "select id, wkn, delta_stck, delta_datum, preis_stck, bemerkung, delta_stck*preis_stck as order_summe " \
              "from delta " \
              "where wkn = '%s' " \
              "order by delta_datum desc " % wkn
        deltalist = self.readAllGetObjectList( sql, XDelta )
        return deltalist

    def getAllMyTickers( self ) -> List[str]:
        sql = "select ticker " \
              "from depotposition pos " \
              "where flag_displ = 1 "
        tupleList = self.read( sql )
        tickerlist = [tpl[0] for tpl in tupleList]
        return tickerlist


def test():
    data = InvestMonitorData()
    #l = data.getDepotPositions()
    strlist = data.getAllMyTickers()
    print( strlist )
    deltalist = data.getDeltas( "WTEM.DE" )
    print( deltalist )
