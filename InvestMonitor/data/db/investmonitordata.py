from typing import List

from base.databasecommon2 import DatabaseCommon
from interface.interfaces import XDepotPosition, XDelta
from imon.definitions import DATABASE


class InvestMonitorData( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self, DATABASE )

    def getDepotPositions( self ) -> List[XDepotPosition]:
        sql = "select pos.id, isin, ticker, wkn, basic_index, name, gattung, waehrung, flag_acc, beschreibung, " \
              "toplaender, topsektoren, topfirmen, " \
              "dep.id as depot_id, dep.bank, dep.nr as depot_nr, dep.vrrkto as depot_vrrkto " \
              "from depotposition pos " \
              "inner join depot dep on dep.id = pos.depot_id " \
              "where flag_displ = 1 " \
              "order by wkn "
        xlist = self.readAllGetObjectList( sql, XDepotPosition )
        return xlist

    def getDepotPosition( self, ticker:str ) -> XDepotPosition:
        sql = "select pos.id, isin, ticker, wkn, basic_index, name, gattung, waehrung, flag_acc, beschreibung, " \
              "toplaender, topsektoren, topfirmen, " \
              "dep.id as depot_id, dep.bank, dep.nr as depot_nr, dep.vrrkto as depot_vrrkto " \
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

    def getAllDeltas( self ) -> List[XDelta]:
        sql = "select delta.id, delta.delta_stck, delta.delta_datum, delta.preis_stck, " \
              "delta.bemerkung, delta_stck*preis_stck as order_summe, " \
              "dp.name, dp.depot_id, delta.wkn, dp.isin, dp.ticker " \
              "from delta delta " \
              "inner join depotposition dp on dp.wkn = delta.wkn " \
              "order by delta.delta_datum desc, delta.id desc "
        deltalist = self.readAllGetObjectList( sql, XDelta )
        return deltalist

    def getAllMyTickers( self ) -> List[str]:
        sql = "select ticker " \
              "from depotposition pos " \
              "where flag_displ = 1 "
        tupleList = self.read( sql )
        tickerlist = [tpl[0] for tpl in tupleList]
        return tickerlist

    def insertDelta( self, delta:XDelta ):
        if not delta.bemerkung: bemerkung = "NULL"
        else: bemerkung = "'%s'" % delta.bemerkung
        sql = "insert into delta " \
              "(wkn, delta_stck, delta_datum, preis_stck, bemerkung) " \
              "values " \
              "( '%s', %d, '%s', %.3f, %s )" % ( delta.wkn, delta.delta_stck, delta.delta_datum, delta.preis_stck, bemerkung )
        self.write( sql )


def test():
    data = InvestMonitorData()
    li = data.getAllDeltas()
    print( li )
    #l = data.getDepotPositions()
    strlist = data.getAllMyTickers()
    print( strlist )
    deltalist = data.getDeltas( "WTEM.DE" )
    print( deltalist )
