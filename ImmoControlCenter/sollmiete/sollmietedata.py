from typing import List, Dict

from databasecommon import DatabaseCommon
from interfaces import XSollMiete
from transaction import BEGIN_TRANSACTION, ROLLBACK_TRANSACTION, COMMIT_TRANSACTION


class SollmieteData( DatabaseCommon ):
    def __init__( self ):
        DatabaseCommon.__init__( self )

    def getCurrentSollmiete( self, mv_id:str ) -> XSollMiete:
        """
        Liefert die letzte (jüngste) Sollmiete für <mv_id>.
        Diese Sollmiete kann auch schon inaktiv sein (<bis> kleiner als current date).
        :param mv_id:
        :return:
        """
        sql = "select sm_id, mv_id, von, von, coalesce(bis, '') as bis, netto, nkv, bemerkung " \
              "from sollmiete " \
              "where mv_id = '%s' " \
              "order by von desc " % mv_id
        dictlist:List[Dict] = self.readAllGetDict( sql )
        d = dictlist[0]
        x = XSollMiete( d )
        return x

    def insertSollmiete( self, x: XSollMiete ) -> int:
        bis = "NULL" if not x.bis else "'" + x.bis + "'"
        sql = "insert into sollmiete " \
              "(mv_id, von, bis, netto, nkv, bemerkung ) " \
              "values( '%s', '%s', %s, %.2f, %.2f, '%s' ) " % (x.mv_id, x.von, bis, x.netto, x.nkv, x.bemerkung)
        return self.write( sql )

    def updateSollmiete( self, x: XSollMiete ):
        """
        Macht einen Update auf genau einen Satz in <sollmiete>.
        !!!Beachte: Die mv_id kann mit dieser Methode nicht geändert werden!!!
        Denn: bei Änderung der mv_id können mehrere Sätze in <sollmiete> betroffen sein,
        es wäre komplett sinnlos, nur einen davon zu ändern.
        :param x:
        :param commit:
        :return:
        """
        bis = "NULL" if not x.bis else "'" + x.bis + "'"
        sql = "update sollmiete set " \
              "von = '%s', " \
              "bis = %s, " \
              "netto = %.2f, " \
              "nkv = %.2f, " \
              "bemerkung = '%s' " \
              "where sm_id = %d" % (x.von, bis, x.netto, x.nkv, x.bemerkung, x.sm_id)
        return self.write( sql )

    def terminateSollmiete( self, sm_id:int, bis:str ) -> int:
        """
        Beendet die Gültigkeit eines Sollmiete-Intervalls
        :param sm_id: Spezifikation des Satzes, dessen Gültigkeit terminiert werden soll
        :param bis: Ende-Datum des Intervalls
        :return:
        """
        sql = "update sollmiete " \
              "set bis = '%s' " \
              "where sm_id = %d " % ( bis, sm_id )
        return self.write( sql )

def test():
    x = XSollMiete()
    x.mv_id = "test_duempfel"
    x.von = "2021-11-11"
    x.netto = 450
    x.nkv = 100

    x2 = XSollMiete()
    x2.mv_id = "anger_inge"
    x2.von = "2021-11-12"
    x2.netto = 300
    x2.nkv = 80

    data = SollmieteData()
    BEGIN_TRANSACTION()
    data.insertSollmiete( x )
    COMMIT_TRANSACTION()
    BEGIN_TRANSACTION()
    data.insertSollmiete( x2 )
    ROLLBACK_TRANSACTION()

