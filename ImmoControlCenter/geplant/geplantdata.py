
from typing import List

from base.databasecommon import DatabaseCommon
from interfaces import XGeplant


class GeplantData( DatabaseCommon ):
    """
    Datenzugriffe auf die Tabelle <geplant>
    """
    def __init__(self):
        DatabaseCommon.__init__( self )

    def getPlanungen( self, jahr:int=None ) -> List[XGeplant]:
        sql = "select id, master_id, mobj_id, leistung, firma, kosten, kostenvoranschlag, jahr, monat, " \
              "beauftragt, erledigtam, bemerkung " \
              "from geplant "
        if jahr:
            sql += "where jahr = %d" % jahr
        objlist = self.readAllGetObjectList( sql, XGeplant )
        return objlist

    def getDistinctYears( self ) -> List[int]:
        sql = "select distinct jahr " \
              "from geplant"
        tuplelist = self.read( sql )
        intlist = [t[0] for t in tuplelist]
        return intlist

    def insertPlanung( self, x:XGeplant ) -> int:
        """
        Fügt eine neue Planung in die Tabelle <geplant> ein und versorgt x.id mit der neu
        vergebenen ID
        :param x:
        :return:
        """
        sql = "insert into geplant " \
              "(master_id, mobj_id, leistung, firma, kosten, kostenvoranschlag, jahr, monat, beauftragt, erledigtam, bemerkung) " \
              "values" \
              "(%d,         '%s',      '%s',   '%s',   %.2f,     %d,              %d,   %d,     %d,         '%s',      '%s')" % \
              (x.master_id, x.mobj_id, x.leistung, x.firma, x.kosten, x.kostenvoranschlag, x.jahr, x.monat, x.beauftragt, x.erledigtDatum, x.bemerkung)
        rowcount = self.write( sql )
        x.id = self.getMaxId( "geplant", "id" )
        return rowcount


def test():
    data = GeplantData()
    res = data.getDistinctYears()
    print( res )