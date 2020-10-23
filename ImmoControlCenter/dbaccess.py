import sqlite3
from typing import List, Tuple, Dict


# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

class DbAccess:
    def __init__( self ):
        self._con = None
        self._cursor = None

    def open( self ) -> None:
        self._con = sqlite3.connect( 'immo.db' )
        self._cursor = self._con.cursor()

    def close( self ) -> None:
        self._cursor.close()
        self._con.close()

    def getMaxId( self, table:str, id_name:str ) -> int:
        sql = "select max(%s) from %s" %(id_name, table)
        records = self._doRead( sql )
        return records[0][0]

    def commit( self ):
        self._con.commit()

    def getMietzahlungen( self, jahr:int ) -> List[Dict]:
        sql = "select mv.von, coalesce( mv.bis, '') as bis, mv.mietobjekt_id as objekt, mv.name || ', ' || mv.vorname as name, " \
               "soll.netto_miete + soll.nk_voraus as soll, " \
               "'ok' as ok, 'nok' as nok, " \
	           "jan, feb, mrz, apr, mai, jun, jul, aug, sept, okt, nov, dez, " \
               " (coalesce(jan,0)+coalesce(feb,0)+coalesce(mrz,0)+coalesce(apr,0)+coalesce(mai,0)+coalesce(jun,0)" \
               "+coalesce(jul,0)+coalesce(aug,0)+coalesce(sept,0)+coalesce(okt,0)+coalesce(nov, 0) + coalesce(dez, 0)) as summe " \
               "from mietverhaeltnis mv " \
               "inner join sollmiete soll on soll.mietobjekt_id = mv.mietobjekt_id " \
	           "inner join mtleinaus ea on ea.mietobjekt_id = mv.mietobjekt_id " \
	           "where ea.jahr = %d " \
	           "and ea.einausart = 'miete' " \
	           "and (mv.bis = '' or mv.bis is NULL or substr(mv.bis, 0, 5) >= '%d') " \
	           "order by name" % ( jahr, jahr )
        diclist: List[Dict] = self._doReadAllGetDict(sql)
        return diclist

    def _doRead( self, sql:str ) -> List[Tuple]:
        self._cursor.execute( sql )
        records = self._cursor.fetchall()
        return records

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _doReadOneGetDict( self, sql:str ) -> Dict or None:
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        return cur.fetchone()

    def _doReadAllGetDict( self, sql:str ) -> Dict or None:
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        return cur.fetchall()

    def _doWrite( self, sql:str, commit:bool ) -> int:
        c = self._cursor.execute( sql )
        if commit:
            self._con.commit()
        return c.rowcount

# =============================================================================
# crsr.execute("CREATE TABLE employees( \
#                  id integer PRIMARY KEY, \
#                  name text, \
#                  salary real, \
#                  department text, \
#                  position text, \
#                  hireDate text)")
#
# con.commit()
# =============================================================================

def test():
    db = DbAccess()
    db.open()

    #diclist:List[Dict] = db.getObjekte( 1 )
    diclist = db.getMietzahlungen( 2020 )
    for dic in diclist:
        for k, v in dic.items():
            print( k, ": ", v)

    # dic:Dict = db.getErhaltungsAufwand( 11, 2015 )
    # if dic is None: print( "Keinen Satz gefunden")
    # else:
    #     for k, v in dic.items():
    #         print( k, ": ", v)

    #max = db.insertErhaltungsaufwand( 1, 2014, voll_abziehbar=1234, zu_verteilen_gesamt_neu=32100, verteilen_auf_jahre=4, abziehbar_vj=8000)
    #db.updateErhaltungsaufwand2( 11, 2015, voll_abziehbar=1234, zu_verteilen_gesamt_neu=9876, verteilen_auf_jahre=5,
    #                             abziehbar_vj=987, abziehbar_vj_minus_1=1,abziehbar_vj_minus_2=2, abziehbar_vj_minus_3=3,abziehbar_vj_minus_4=4)
    db.close()

if __name__ == '__main__':
    test()