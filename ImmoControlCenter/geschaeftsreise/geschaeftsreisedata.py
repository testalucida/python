from typing import List

from databasecommon import DatabaseCommon
from interfaces import XGeschaeftsreise


class GeschaeftsreiseData( DatabaseCommon ):
    def __init__(self):
        DatabaseCommon.__init__( self )

    def getDistinctJahre( self ) -> List[int]:
        sql = "select distinct jahr from geschaeftsreise order by jahr desc "
        tuplelist = self.read( sql )
        jahre = [t[0] for t in tuplelist]
        return jahre

    def getAllGeschaeftsreisen( self, jahr:int ) -> List[XGeschaeftsreise]:
        sql = "select id, mobj_id, von, bis, jahr, ziel, zweck, km, personen, " \
              "uebernachtung, uebernacht_kosten " \
              "from geschaeftsreise " \
              "where jahr = %d" % jahr
        return self.readAllGetObjectList( sql, XGeschaeftsreise )

    def getGeschaeftsreisen( self,  master_name:str, jahr:int ) -> List[XGeschaeftsreise]:
        """
        Ermittelt alle Geschäftsreisen zu einem Masterobjekt.
        Da die Geschäftsreisen zu einer mobj_id erfasst sind, wird über zwei inner joins gesammelt.
        Diese Methode wird für die Anlage V gebraucht, da diese sich auf Masterobjekte bezieht.
        :param master_name:
        :param jahr:
        :return:
        """
        sql = "select id, master.master_id, master.master_name, " \
              "g.mobj_id, von, bis, jahr, ziel, zweck, km, personen, " \
              "uebernachtung, uebernacht_kosten " \
              "from geschaeftsreise g " \
              "inner join mietobjekt mobj on mobj.mobj_id = g.mobj_id " \
              "inner join masterobjekt master on master.master_id = mobj.master_id " \
              "where master.master_name = '%s' " \
              "and jahr = %d " % ( master_name, jahr )
        xlist = self.readAllGetObjectList( sql, XGeschaeftsreise )
        return xlist

    def insertGeschaeftsreise( self, x:XGeschaeftsreise ) -> int:
        uebernachtung = x.uebernachtung if x.uebernachtung > " " else ""
        uebernacht_kosten = x.uebernacht_kosten if x.uebernacht_kosten > 0 else 0.0
        sql = "insert into geschaeftsreise " \
              "( mobj_id, jahr, von, bis, ziel, " \
              "zweck, km, personen, uebernachtung, uebernacht_kosten )" \
              "values" \
              "( '%s', %d, '%s', '%s', '%s'," \
              "  '%s', %d, %d, '%s', %.2f )" % (x.mobj_id, x.jahr, x.von, x.bis, x.ziel,
                                                  x.zweck, x.km, x.personen,
                                                  uebernachtung, uebernacht_kosten )
        return self.write( sql )

    def updateGeschaeftsreise( self, x:XGeschaeftsreise ) -> int:
        sql = "update geschaeftsreise " \
              "set mobj_id = '%s', " \
              "von = '%s', " \
              "bis = '%s', " \
              "ziel = '%s', " \
              "zweck = '%s', " \
              "km = %d, " \
              "personen = %d, " \
              "uebernachtung = '%s', " \
              "uebernacht_kosten = %.2f " \
              "where id = %d " % ( x.mobj_id, x.von, x.bis, x.ziel, x.zweck, x.km,
                                   x.personen, x.uebernachtung, x.uebernacht_kosten, x.id )
        return self.write( sql )

    def deleteGeschaeftsreise( self, id:int, commit:bool=True ) -> int:
        sql = "delete from geschaeftsreise where id = %d " % id
        return self.write( sql )


def test2():
    data = GeschaeftsreiseData()
    jahre = data.getDistinctJahre()
    print( jahre )

def test1():
    data = GeschaeftsreiseData()
    xlist = data.getGeschaeftsreisen( "ILL_Eich", 2021 )
    #xlist = data.getGeschaeftsreisen( "N_Mendel", 2021 )
    print( xlist )