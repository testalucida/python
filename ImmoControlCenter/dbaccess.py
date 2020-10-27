import sqlite3
from typing import List, Tuple, Dict
mon_dbnames = ("jan", "feb", "mrz", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "dez" )

# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

class DbAccess:
    def __init__( self, dbname:str ):
        self._con = None
        self._cursor = None
        self._dbname = dbname

    def open( self ) -> None:
        self._con = sqlite3.connect( self._dbname )
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

    def getMietobjekte(self) -> List:
        sql = "select id from mietobjekt where aktiv = 1"
        listoftuples = self._doRead( sql )
        return [x[0] for x in listoftuples]

    def getMietzahlungen( self, jahr:int ) -> List[Dict]:
        sql = "select mv.von, coalesce( mv.bis, '') as bis, mv.mietobjekt_id as objekt, mv.name || ', ' || mv.vorname as name, " \
               "soll.netto_miete + soll.nk_voraus as soll, " \
               "'ok' as ok, 'nok' as nok, " \
	           "jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez, " \
               " (coalesce(jan,0)+coalesce(feb,0)+coalesce(mrz,0)+coalesce(apr,0)+coalesce(mai,0)+coalesce(jun,0)" \
               "+coalesce(jul,0)+coalesce(aug,0)+coalesce(sep,0)+coalesce(okt,0)+coalesce(nov, 0) + coalesce(dez, 0)) as summe " \
               "from mietverhaeltnis mv " \
               "inner join sollmiete soll on soll.mietobjekt_id = mv.mietobjekt_id " \
	           "inner join mtleinaus ea on ea.mietobjekt_id = mv.mietobjekt_id " \
	           "where ea.jahr = %d " \
	           "and ea.einausart = 'miete' " \
	           "and (mv.bis = '' or mv.bis is NULL or substr(mv.bis, 0, 5) >= '%d') " \
	           "order by name" % ( jahr, jahr )
        diclist: List[Dict] = self._doReadAllGetDict(sql)
        return diclist

    def getSollmieten( self, jahr:int ):
        """liefert alle im jahr aktiven Mietobjekte mit den in diesem Jahr gültigen Sollmieten.
            Je Objekt werden soviele Sollmieten geliefert, wie in diesem Jahr gültig waren.
            Die Daten werden in Form eines Dictionary geliefert:
            {
                "charlotte": (
                                {
                                    "von": "2019-03-01"
                                    "bis": "2019-12-31"
                                    "netto_miete": 300
                                    "nk_voraus": 150
                                },
                                {
                                    "von": "2020-02-01"  ##beachte: Zeitenräume können Lücken enthalten (Leerstand)
                                    "bis": ""
                                    "netto_miete": 350
                                    "nk_voraus": 150
                                }
                             )
            }
        """
        sjahr = str( jahr )
        sql = "select mietobjekt_id, von, bis, netto-miete, nk_voraus " \
              "from sollmiete " \
              "where substr(von, 0, 5)  <= %s " \
              "and ( bis is null or bis = '' or substr(bis, 0, 5) >= %s "


    def insertMietverhaeltnis( self, d:Dict, commit:bool=True ) -> int:
        sql = "insert into mietverhaeltnis " \
              "(mietobjekt_id, von, bis, name, vorname, telefon, mobil, mailto, anzahl_pers, mietkonto, bemerkung1, bemerkung2) " \
              "values " \
              "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s') " % \
              (d["Objekt"].lower(), d["von"], d["bis"], d["Name"], d["Vorname"], "", d["mobil"], d["mailto"], d["anzpers"],
               d["Mietkonto"], d["Bemerkung1"], d["Bemerkung2"])
        return self._doWrite( sql, commit )

    def insertSollmiete(self, d:Dict, commit:bool=True ) -> int:
        sql = "insert into sollmiete " \
              "(mietobjekt_id, von, bis, netto_miete, nk_voraus ) " \
              "values( '%s', '%s', '%s', %f, %f ) " % ( d["mietobjekt_id"], d["von"], d["bis"], d["netto_miete"], d["nk_voraus"] )
        return self._doWrite( sql, commit )

    def existsEinAusArt(self, einausart:str, jahr:int ) -> bool:
        sql = "select count(*) as anz from mtleinaus where einausart = '%s' and jahr = %d " % ( einausart, jahr )
        d = self._doReadOneGetDict( sql )
        return d["anz"] > 0

    def insertMtlEinAus(self, mietobjekt_id:str, einausart:str, jahr:int, commit:bool=True ) -> int:
        """
        legt einen Satz in der Tabelle mtleinaus an, wobei alle Monatswerte auf 0 gesetzt werden
        :param mietobjekt_id:
        :param einausart:
        :param jahr:
        :param commit:
        :return:
        """
        sql = "insert into mtleinaus (mietobjekt_id, einausart, jahr) values ('%s', '%s', %d) " \
              % (mietobjekt_id, einausart, jahr)
        return self._doWrite(sql, commit)

    def insertMtlEinAus2(self, d:Dict ) -> int:
        """
        legt einen Satz in der Tabelle mtleinaus an.
        :param d:
        :return:
        """
        pass

    def updateMtlEinAus( self, mietobjekt_id:str, einausart:str, jahr:int, monat:int or str, value:float, commit:bool=True ) -> int:
        """
        Ändert einen Monatswert in der Tabelle mtleinaus
        :param mietobjekt_id: identifz. das Mietobjekt
        :param einausart:  identifiziert die einausart
        :param jahr:  identifiziert das Jahr
        :param monat: identifiziert den Monat: 1 -> Januar, ..., 12 -> Dezember oder als string "jan",..."dez"
        :param value: der Wert, der im betreffenden Monat eingetragen werden soll
        :return:
        """
        sql = "update mtleinaus set "
        sql += ( mon_dbnames[monat-1] if isinstance( monat, int ) else monat )
        sql += " = %f where mietobjekt_id = '%s' and einausart = '%s' and jahr = %d " \
               % ( value, mietobjekt_id, einausart, jahr )
        return self._doWrite( sql, commit )

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
    db.open( "immo_TEST.db" )

    l = db.getMietobjekte()

    #db.insertMtlEinAus( "bueb", "miete", 2021 )

    db.updateMtlEinAus( "bueb", "miete", 2020, "feb", 999 )
    #
    # #diclist:List[Dict] = db.getObjekte( 1 )
    # diclist = db.getMietzahlungen( 2020 )
    # for dic in diclist:
    #     for k, v in dic.items():
    #         print( k, ": ", v)

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