from typing import List, Dict

from anlage_v.anlagev_interfaces import XObjektStammdaten, XZeilendefinition
from dbaccess import DbAccess
from interfaces import XSollMiete


class AnlageV_DataAccess( DbAccess ):
    def __init__( self, dbname:str ):
        DbAccess.__init__( self, dbname )

    def getAnlageV_Zeilendefinitionen( self ) -> List[XZeilendefinition]:
        sql = "select feld_nr, feld_id, zeile, printX, printY from anlagev_layout order by feld_nr "
        dictlist = self._doReadAllGetDict( sql )
        li:List[XZeilendefinition] = list()
        for dic in dictlist:
            x = XZeilendefinition( dic )
            li.append( x )
        return li

    def getSteuerpflichtige( self ) -> List[Dict]:
        """
        liefert alle Steuerpflichtigen aus Tabelle steuerpflichtiger
        in einem Dictionary mit den Keys name, vorname, steuernummer
        :return: List[Dict]
        """
        sql = "select name, vorname, steuernummer from steuerpflichtiger order by name "
        ld = self._doReadAllGetDict( sql )
        return ld

    def getObjektNamen( self ) -> List[str]:
        sql = "select master_name from masterobjekt " \
              "where master_name not like '*%' " \
              "order by master_name "
        tuplelist = self._doRead( sql )
        names = [e[0] for e in tuplelist]
        return names

    def getObjektStammdaten( self ) -> List[XObjektStammdaten]:
        sql = "select master_id, master_name, strasse_hnr, plz, ort, angeschafft_am, veraeussert_am, gesamt_wfl, einhwert_az " \
              "from masterobjekt " \
              "where master_name not like '*%'"
        diclist = self._doReadAllGetDict( sql )
        li:List[XObjektStammdaten] = list()
        for dic in diclist:
            x = XObjektStammdaten( dic )
            li.append( x )
        return li

    def getMasterobjektJahresBruttomieteSumme( self, master_id:int, jahr:int ) -> float:
        # liefert die Jahresbruttomieeinnahmen eines Masterobjekts in *einer* Summe
        sql = "select sum( coalesce(jan,0) +  coalesce(feb, 0) + coalesce(mrz, 0) + coalesce(apr, 0) + coalesce(mai, 0) + coalesce(jun, 0) + " \
              "coalesce(jul, 0) + coalesce(aug, 0) + coalesce(sep, 0) + coalesce(okt, 0) + coalesce(nov, 0) + coalesce(dez, 0) ) as masterobjekt_jahressumme " \
              "from mietobjekt mobj " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join mtleinaus mea on mea.mv_id = mv.mv_id " \
              "where mobj.master_id = %d " \
              "and mea.jahr = %d " % (master_id, jahr)
        listoftuples = self._doRead( sql )
        return listoftuples[0][0]

    def getMasterobjektBruttomieten( self, master_id:int, jahr:int ) -> List[Dict]:
        # liefert die Jahresbruttomieteinnahmen je Mieter als Liste von Dictionaries.
        # Jeder Dictionary hat den Aufbau
        # {
        #    'mv_id': 'bucher_lothar'
        #    'brutto_me:': 780.0
        # }
        sql = "select mv.mv_id, coalesce(jan,0) +  coalesce(feb, 0) + coalesce(mrz, 0) + coalesce(apr, 0) + coalesce(mai, 0) + coalesce(jun, 0) + " \
              "coalesce(jul, 0) + coalesce(aug, 0) + coalesce(sep, 0) + coalesce(okt, 0) + coalesce(nov, 0) + coalesce(dez, 0) as brutto_me " \
              "from mietobjekt mobj " \
              "inner join mietverhaeltnis mv on mv.mobj_id = mobj.mobj_id " \
              "inner join mtleinaus mea on mea.mv_id = mv.mv_id " \
              "where mobj.master_id = %d " \
              "and mea.jahr = %d " % (master_id, jahr)
        dictlist = self._doReadAllGetDict( sql )
        return dictlist

    def getSollmieten3( self, mv_id:str, jahr:int ) -> List[XSollMiete]:
        # liefert die Sollmieten für Mieter mv_id im Jahr jahr
        minbis = "%d-%02d-%02d" % (jahr, 1, 1)
        maxvon = "%d-%02d-%02d" % (jahr+1, 1, 1)
        sql = "select sm.sm_id, sm.mv_id, sm.von, coalesce(sm.bis, '') as bis, sm.netto, sm.nkv, (sm.netto + sm.nkv) as brutto, " \
              "coalesce(sm.bemerkung, '') as bemerkung, mv.mobj_id " \
              "from sollmiete sm " \
              "inner join mietverhaeltnis mv on mv.mv_id = sm.mv_id " \
              "where sm.von < '%s' " \
              "and (sm.bis is NULL or sm.bis = '' or sm.bis >= '%s') " \
              "and sm.mv_id = '%s' " \
              "order by sm.mv_id, sm.von desc" % ( maxvon, minbis, mv_id )
        l: List[Dict] = self._doReadAllGetDict( sql )
        sollList: List[XSollMiete] = list()
        for d in l:
            x = XSollMiete( d )
            sollList.append( x )
        return sollList

def test():
    av = AnlageV_DataAccess( "../immo.db")
    av.open()

    names = av.getObjektNamen()
    print( names )

    #li = db.getSollmieten2( 2020 )

    li = av.getSollmieten3( "bucher_lothar", 2020 )

    dictlist = av.getMasterobjektBruttomieten( 17, 2021 )
    print( dictlist )

    av.close()

if __name__ == '__main__':
    test()