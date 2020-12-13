import sqlite3
from typing import List, Tuple, Dict
from constants import einausart
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

    def getMietobjekteKurz( self ) -> List[Dict]:
        """
        Liefert folgende Informationen für alle aktiven Mietobjekte:
        - mobj_id
        - master_id
        :return:
        """
        sql = "select mobj_id, master_id " \
              "from mietobjekt " \
              "where aktiv = 1 " \
              "order by mobj_id "
        return self._doReadAllGetDict( sql )

    def getMasterUndMietobjekte( self ) -> List[Dict]:
        """
        Liefert Informationen aus einem Join von masterobjekt und mietobjekt
        :return:
        """
        sql = "select ma.master_id, ma.name, mi.mobj_id, mi.whg_bez " \
              "from masterobjekt ma " \
              "inner join mietobjekt mi on mi.master_id = ma.master_id " \
              "where mi.aktiv = 1 " \
              "order by ma.master_id, mi.mobj_id "
        return self._doReadAllGetDict( sql )

    def getMietverhaeltnisseEssentials( self, jahr:int ) -> List[Dict]:
        """
        Liefert zu allen Mietverhältnissen, die in <jahr> aktiv sind, die Werte der Spalten mv_id, von, bis
        :param jahr:
        :return: List[Dict]:
                [
                    {
                        "mv_id":  "landeranke",
                        "von":    "2019-01-01"
                        "bis":    ""
                    },
                    ...
                ]
        """
        sql = "select mv_id, von, bis from mietverhaeltnis " \
              "where substr(von, 0, 5) <= '%s' " \
              "and (bis is NULL or bis = '' or substr(bis, 0, 5) >= '%s')" % (jahr, jahr)
        return self._doReadAllGetDict( sql )

    def getMietzahlungenMitSummen( self, jahr:int ) -> List[Dict]:
        # Achtung: das TableModel verlässt sich auf die Reihenfolge der Spalten.
        # Wenn sie geändert wird, muss man das im CheckTableModel.__init()__ anpassen.
        sql = "select ea.meinaus_id, mv.mv_id, " \
              "mv.von, coalesce( mv.bis, '') as bis, mv.mobj_id as objekt, mv.name || ', ' || mv.vorname as name, " \
              "0 as soll, " \
              "'ok' as ok, 'nok' as nok, " \
              "jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez, " \
              "(coalesce(jan,0)+coalesce(feb,0)+coalesce(mrz,0)+coalesce(apr,0)+coalesce(mai,0)+coalesce(jun,0)+" \
              "coalesce(jul,0)+coalesce(aug,0)+coalesce(sep,0)+coalesce(okt,0)+coalesce(nov, 0) + coalesce(dez, 0)) as summe " \
              "from mietverhaeltnis mv " \
              "inner join mtleinaus ea on ea.mv_id = mv.mv_id " \
              "where ea.jahr = %s " \
              "and ea.mv_id > '' " \
              "and (mv.bis = '' or mv.bis is NULL or substr(mv.bis, 0, 5) >= '%s') " \
	          "order by mv.mv_id" % ( jahr, jahr )
        diclist: List[Dict] = self._doReadAllGetDict(sql)
        return diclist

    def getVerwaltungen( self, jahr:int ) -> List[Dict]:
        vgldat = str(jahr) + "-01-01"
        sql = "select vwg_id, mobj_id, vw_id, weg_name, von, coalesce( bis, '' ) as bis " \
              "from verwaltung " \
              "where von <= '%s' and (bis is NULL or bis = '' or bis > '%s')" % (vgldat, vgldat)
        diclist: List[Dict] = self._doReadAllGetDict( sql )
        return diclist

    def getHausgeldvorauszahlungenMitSummen( self, jahr:int ) -> List[Dict]:
        # Achtung: das TableModel verlässt sich auf die Reihenfolge der Spalten.
        # Wenn sie geändert wird, muss man das im CheckTableModel.__init()__ anpassen.
        sql = "select ea.meinaus_id, vwg.vwg_id, " \
              "vwg.von, coalesce( vwg.bis, '') as bis, vwg.mobj_id as objekt, vwg.weg_name || ' / ' || vwg.vw_id as name, " \
              "0 as soll, " \
              "'ok' as ok, 'nok' as nok, " \
              "jan, feb, mrz, apr, mai, jun, jul, aug, sep, okt, nov, dez, " \
              "(coalesce(jan,0)+coalesce(feb,0)+coalesce(mrz,0)+coalesce(apr,0)+coalesce(mai,0)+coalesce(jun,0)+" \
              "coalesce(jul,0)+coalesce(aug,0)+coalesce(sep,0)+coalesce(okt,0)+coalesce(nov, 0) + coalesce(dez, 0)) as summe " \
              "from verwaltung vwg " \
              "inner join mtleinaus ea on ea.vwg_id = vwg.vwg_id " \
              "where ea.jahr = %s " \
              "and ea.vwg_id > 0 " \
              "and (vwg.bis = '' or vwg.bis is NULL or substr(vwg.bis, 0, 5) >= '%s') " \
              "order by vwg.weg_name" % (jahr, jahr)
        diclist: List[Dict] = self._doReadAllGetDict( sql )
        return diclist

    def getSollmieten( self, jahr:int ) -> List[Dict]:
        sjahr = str( jahr )
        sql = "select mv_id, von, bis, netto, nkv, netto+nkv as brutto " \
              "from sollmiete " \
              "where substr(von, 0, 5)  <= '%s' " \
              "and ( bis is null or bis = '' or substr(bis, 0, 5) >= '%s' ) " \
              "order by mv_id, von;" % ( sjahr, sjahr )
        l = self._doReadAllGetDict( sql )
        return l

    def getSollmietenMonat( self, jahr:int, monat:int ) -> List[Dict]:
        datum = str(jahr) + "-" + "%02d" % monat + "-01"
        sql = "select mv_id, von, bis, netto, nkv, netto+nkv as brutto " \
              "from sollmiete " \
              "where von <= '%s' " \
              "and (bis is NULL or bis = '' or bis > '%s') " \
              "order by mv_id" % (datum, datum)
        return self._doReadAllGetDict( sql )

    def getSollHausgelderMonat( self, jahr:int, monat:int ) -> List[Dict]:
        datum = str( jahr ) + "-" + "%02d" % monat + "-01"
        sql = "select vwg_id, von, coalesce(bis, '') as bis, netto, ruezufue " \
              "from sollhausgeld " \
              "where von <= '%s' " \
              "and (bis is NULL or bis = '' or bis > '%s') " \
              "order by vwg_id" % (datum, datum)
        return self._doReadAllGetDict( sql )

    def getJahre( self, eaart:einausart ) -> List[int]:
        id = "mv_id" if eaart == einausart.MIETE else "vwg_art"
        sql = "select distinct jahr from mtleinaus where %s > 0 " % ( id )
        rowlist = self._doRead( sql )
        list = [x[0] for x in rowlist]
        return list

    def getKreditoren( self, master_name:str ) -> List[str]:
        sql = "select distinct kreditor " \
              "from kreditorleistung k " \
              "inner join masterobjekt m on m.master_id = k.master_id " \
              "where m.name = '%s' " \
              "order by kreditor " % ( master_name )
        rowlist = self._doRead( sql )
        list = [x[0] for x in rowlist]
        list = sorted( list, key=str.casefold )
        return list

    # def getServiceleistungen( self ) -> List[Dict]:
    #     sql = "select service.kreditor, service.master_id, master.name, service.mobj_id, service.buchungstext, service.umlegbar " \
    #           "from serviceleistung service " \
    #           "inner join masterobjekt master on master.master_id = service.master_id " \
    #           "order by kreditor, buchungstext "
    #     dictlist = self._doReadAllGetDict( sql )
    #     return dictlist

    def getMasterobjekte( self ) -> List[Dict]:
        sql = "select master_id, name " \
              "from masterobjekt " \
              "order by name "
        dictlist = self._doReadAllGetDict( sql )
        return dictlist



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
              "(mv_id, von, bis, netto, nkv ) " \
              "values( '%s', '%s', '%s', %f, %f ) " % ( d["mv_id"], d["von"], d["bis"], d["netto"], d["nkv"] )
        return self._doWrite( sql, commit )

    def insertSollhausgeld( self, d:Dict, commit:bool=True ) -> int:
        bis = "NULL" if not d["bis"] else "'" + d["bis"] + "'"
        sql = "insert into sollhausgeld " \
              "(vwg_id, von, bis, netto, ruezufue) " \
              "values( '%s', '%s', %s, %f, %f ) " % ( d["vwg_id"], d["von"], bis, d["netto"], d["ruezufue"] )
        return self._doWrite( sql, commit )

    def insertServiceleistung( self, name:str, mobj_id:str, buchungstext:str, umlegbar:int=0, commit:bool=True ):
        if buchungstext is None: buchungstext = ""
        sql = "insert into serviceleistung " \
              "(name, mobj_id, buchungstext, umlegbar) " \
              "values" \
              "('%s', '%s', '%s', %d) " % ( name, mobj_id, buchungstext, umlegbar )
        return self._doWrite( sql, commit )

    def existsEinAusArt(self, eaart:einausart, jahr:int ) -> bool:
        id = "mv_id" if eaart == einausart.MIETE else "vwg_id"
        sql = "select count(*) as anz from mtleinaus where jahr = %d and %s is not null" % ( jahr, id )
        d = self._doReadOneGetDict( sql )
        return d["anz"] > 0

    def insertMtlEinAus(self, mv_or_vwg_id:str, eaart:einausart, jahr:int, commit:bool=True ) -> int:
        """
        legt einen Satz in der Tabelle mtleinaus an, wobei alle Monatswerte auf 0 gesetzt werden
        :param id: je nach einausart ist das die mv_id oder die vwg_id
        :param einausart: "miete" oder "hgv"
        :param jahr:
        :param commit:
        :return:
        """
        id = "mv_id" if eaart == einausart.MIETE else "vwg_id"
        sql = "insert into mtleinaus (%s, jahr) values ('%s', %d) " % (id, mv_or_vwg_id, jahr)
        return self._doWrite(sql, commit)

    def insertVerwalter( self, d:Dict, commit:bool=True ) -> int:
        sql = "insert into verwalter " \
              "(vw_id, name, strasse, plz_ort, telefon_1, telefon_2, mailto, ansprechpartner_1, ansprechpartner_2, bemerkung)" \
              "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' )" \
              % (d["vw_id"], d["name"], d["strasse"], d["plz_ort"], d["telefon_1"], d["telefon_2"], d["mailto"],
                 d["ansprechpartner_1"], d["ansprechpartner_2"], d["bemerkung"] )
        return self._doWrite( sql, commit )

    def updateMtlEinAus( self, meinaus_id:str, monat:int or str, value:float, commit:bool=True ) -> int:
        """
        Ändert einen Monatswert in der Tabelle mtleinaus
        :param meinaus_id: identifz. den mtleinaus-Satz, damit auch das Jahr, egal ob Miete oder HGV
        :param monat: identifiziert den Monat: 1 -> Januar, ..., 12 -> Dezember oder als string "jan",..."dez"
        :param value: der Wert, der im betreffenden Monat eingetragen werden soll
        :return:
        """
        dbval = "%.2f" % (value) if value > 0 else "NULL"
        sMonat =  mon_dbnames[monat-1] if isinstance( monat, int ) else monat
        sql = "update mtleinaus set '%s' = %s where meinaus_id = %d  " % ( sMonat, dbval, meinaus_id )
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
    db = DbAccess( "immo_TEST.db" )
    db.open()

    dictlist = db.getMasterUndMietobjekte()
    print( dictlist )
    # dictlist = db.getServiceleistungen()
    # print( dictlist )
    # list = db.getServiceleister()
    # print( list )

    #dictlist = db.getHausgeldvorauszahlungenMitSummen( 2020 )
    #dictlist = db.getSollHausgelderMonat( 2020, 10 )
    #print( dictlist)

    #jahre = db.getJahre( einausart.MIETE )
    #print( jahre )
    #dictlist = db.getSollmietenMonat( 2020, 2 )
    # dictlist = db.getMietzahlungen( 2020 )
    # print( dictlist )
    # d = {
    #     "mv_id": "murasovolga",
    #     "von": "2021-01-01",
    #     "bis": "",
    #     "netto": 490.0,
    #     "nkv": 80.5
    # }
    #db.insertSollmiete( d )
    #dictlist = db.getMietverhaeltnisseEssentials( 2020 )
    #dictlist = db.getMietzahlungen( 2020 )
    # print(db)


    #l = db.getMietobjekte()

    #db.insertMtlEinAus( "engelhardtrene", "miete", 2020 )

    #db.updateMtlEinAus( "bueb", "miete", 2020, "feb", 999 )
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
