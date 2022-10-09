from typing import List, Tuple, Dict

import datehelper
from base.databasecommon2 import DatabaseCommon
from base.interfaces import XBase

from v2.icc.definitions import DATABASE
from v2.icc.constants import EinAusArt
from v2.icc.interfaces import XHandwerkerKurz, XEinAus, XMietverhaeltnisKurz

class DbAction:
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

class IccData( DatabaseCommon ):
    """
    Enthält die DB-Zugriffe für Miet- UND Masterobjekte
    """
    __dbCommon:DatabaseCommon = None # alle IccData-Instanzen sollen mit nur einem DatabaseCommon-Objekt arbeiten
    def __init__(self):
        if not IccData.__dbCommon:
            IccData.__dbCommon = DatabaseCommon.__init__( self, DATABASE )

    def getIccTabellen( self ) -> List[str]:
        sql = "select name from sqlite_master where type = 'table' order by name"
        tupleList = self.read( sql )
        l = [x[0] for x in tupleList]
        return l

    def getJahre( self ) -> List[int]:
        """
        Liefert die Jahreszahlen, zu denen Daten in der Tabelle einaus erfasst sind.
        :return:
        """
        sql = "select distinct jahr " \
              "from einaus " \
              "order by jahr desc "
        l: List[Dict] = self.readAllGetDict( sql )
        return [d["jahr"] for d in l]

    def getMietverhaeltnisseKurz( self, jahr: int, orderby: str = None ) -> List[XMietverhaeltnisKurz]:
        """
        Liefert zu allen Mietverhältnissen, die in <jahr> aktiv sind, die Werte der Spalten mv_id, mobj_id, von, bis.
        Geliefert werden also neben den "Langläufern" MV, die während <jahr> enden und MV, die während MV beginnen.
        :param jahr:
        :param orderby:
        :return:
        """
        sql = "select id, mv_id, mobj_id, von, bis " \
              "from mietverhaeltnis " \
              "where substr(von, 0, 5) <= '%s' " \
              "and (bis is NULL or bis = '' or substr(bis, 0, 5) >= '%s') " % (jahr, jahr)
        if orderby:
            sql += "order by %s " % (orderby)
        return self.readAllGetObjectList( sql, XMietverhaeltnisKurz )

    def getKreditoren( self ) -> List[str]:
        sql = "select distinct kreditor from kreditorleistung order by kreditor "
        tuplelist = self.read( sql )
        return [t[0] for t in tuplelist]

    def getHandwerkerKurz( self, orderby:str=None ) -> List[XHandwerkerKurz]:
        """
        Selektiert alle Handwerkerdaten aus der Tabelle <handwerker>.
        :param orderby: Wenn angegeben, muss der Inhalt dem Spaltennamen entsprechen, nach dem sortiert werden soll.
                        Defaultmäßig wird nach dem Namen sortiert.
        :return:
        """
        if not orderby: orderby = "name"
        sql = "select id, name, branche, adresse from handwerker order by %s " % orderby
        xlist = self.readAllGetObjectList( sql, XHandwerkerKurz )
        return xlist

    def getMastername( self, mobj_id:str ) -> str:
        sql = "select master_name from mietobjekt where mobj_id = '%s' " % mobj_id
        tpl:List[Tuple] = self.read( sql )
        if len( tpl ) == 0:
            return ""
        return tpl[0][0]

    def writeAndLog( self, sql: str, action:str, table:str, id_name:str, id_value:int,
                     newvalues:str=None, oldvalues:str=None ) -> int:
        """
        Führt <sql> aus.
        Veranlasst einen Log-Eintrag in Tabelle <writelog>
        :param sql: die auszuführende Query. Wird im Anschluss in <writelog> eingetragen.
        :param action:  insert, update, delete - gem. class DbAction
        :param table: der Name der Tabelle, die vom Schreibvorgang betroffen ist. Für Log-Zwecke
        :param id_name: der Name der Id in <table>
        :param id_value: der Wert der Id in <table> (Identifikation des zu ändernden/zu löschenden Satzes.
                        Ist 0 im Insert-Fall.)
        :param newvalues: die Werte im String-Format, mit denen der Insert/Update erfolgt. Z.B. ermittelt mit
                          XBase.toString()
        :param oldvalues: die Werte vor dem Update. None bei Insert
        :param commit:
        :return:
        """
        try:
            ret = self.write( sql )
        except Exception as ex:
            msg = "Exception\n" + str(ex) + "\nbei Ausführung des Statements\n" + sql + "\n"
            raise Exception( msg )
        if action == DbAction.INSERT:
            id_value = ret
        self._writeLog( sql, action, table, id_name, id_value, newvalues, oldvalues )


        return ret

    def _writeLog( self, sql:str, action:str, table:str, id_name:str, id_value:int,
                   newvalues:str=None, oldvalues:str=None ):
        sql = sql.replace( "'", "\"" )
        if newvalues:
            newvalues = newvalues.replace( "'", "\"" )
        if oldvalues:
            oldvalues = oldvalues.replace( "'", "\"" )
        ts = datehelper.getCurrentTimestampIso()
        transId = self.getTransactionId()
        sql = "insert into writelog " \
              "(trans_id, sql, action, table_name, id_name, id_value, newvalues, oldvalues, timestamp) " \
              "values " \
              "( %d,      '%s', '%s',  '%s',         '%s',    %d,     '%s',        '%s',      '%s' )" \
              % (transId, sql, action, table,     id_name, id_value, newvalues, oldvalues,    ts )
        try:
            self.write( sql )
        except Exception as ex:
            msg = "Exception\n" + str(ex) + "\nbei Ausführung des Statements\n" + sql + "\n"
            raise Exception( msg )



