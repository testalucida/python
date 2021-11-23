from typing import Dict

from dbaccess import DbAccess
from interfaces import XZahlung


class InitZahlungKostenartEtc:
    def __init__( self ):
        self._db = DbAccess( "/home/martin/Vermietung/ImmoControlCenter/immo.db" )

    def run( self ):
        resp = input( "Diesen Batch wirklich laufen lassen?" )
        if resp not in ("J", "j", "y", "Y" ): return
        self._db.open()
        sql = self._getSql()
        #l = self._db.executeReadSql( sql, "XZahlung", "interfaces"
        l = self._db.executeReadSql( sql )
        for d in l:
            self._updateZahlung( d )
        self._db.commit()
        self._db.close()
        print( "fertig." )

    def _getSql( self ) -> str:
        sql = "select s.saus_id, z.z_id, s.kostenart, s.umlegbar, s.buchungsdatum, s.buchungstext " \
              "from zahlung z " \
              "inner join sonstaus s on s.saus_id = z.saus_id " \
              "where zahl_art = 'sonstaus' "
        return sql

    def _updateZahlung( self, dic:Dict ):
        sql = "update zahlung " \
              "set kostenart = '%s', " \
              "umlegbar = %d, " \
              "buchungsdatum = '%s', " \
              "buchungstext = '%s' " \
              "where z_id = %d" % (dic["kostenart"], dic["umlegbar"], dic["buchungsdatum"], dic["buchungstext"], dic["z_id"] )
        self._db.executeWriteSql( sql, False )

def run():
    batch = InitZahlungKostenartEtc()
    batch.run()

if __name__ == "__main__":
    run()
