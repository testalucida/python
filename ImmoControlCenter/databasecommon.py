import sqlite3
from datetime import datetime
from typing import List, Tuple, Dict, Type

from definitions import DATABASE
from interfaces import XBase, XWertebereich

###########################  DatabaseConnection  ###########################
class DatabaseConnection:
    __instance = None
    def __init__( self ):
        self._con = None
        self._dbname = DATABASE
        self._inTransaction = False

        if DatabaseConnection.__instance:
            raise Exception("DatabaseConnection is a Singleton. You may instantiate it only once." )
        else:
            DatabaseConnection.__instance = self
            self._open()

    @staticmethod
    def inst():
        if not DatabaseConnection.__instance:
            DatabaseConnection()
        return DatabaseConnection.__instance

    def _open( self ):
        self._con = sqlite3.connect( self._dbname )

    def getDbName( self ) -> str:
        return self._dbname

    def getConnection( self ):
        return self._con

    def begin_transaction( self ):
        self._inTransaction = True

    def commit_transaction( self ):
        self._con.commit()
        self._inTransaction = False

    def rollback_transaction( self ):
        self._con.rollback()
        self._inTransaction = False

    def isInTransaction( self ) -> bool:
        return self._inTransaction


###########################  DatabaseCommon  ############################
class DatabaseCommon:
    # __instance = None
    # def __init__( self ):
    #     if DatabaseCommon.__instance:
    #         raise Exception("DatabaseCommon is a Singleton. You may instantiate it only once." )
    #     else:
    #         DatabaseCommon.__instance = self
    #     self._con = None
    #     self._dbname = DATABASE
    #     self._inTransaction = False
    #
    # @staticmethod
    # def inst():
    #     if not DatabaseCommon.__instance:
    #         DatabaseCommon()
    #         DatabaseCommon.inst().open()
    #     return DatabaseCommon.__instance

    # def open( self ):
    #     self._con = sqlite3.connect( self._dbname )

    def __init__( self ):
        self._con = DatabaseConnection.inst().getConnection()
        #self._inTransaction = False

    # def begin_transaction( self ):
    #     self._inTransaction = True
    #
    # def commit_transaction( self ):
    #     self._con.commit()
    #     self._inTransaction = False
    #
    # def rollback_transaction( self ):
    #     self._con.rollback()
    #     self._inTransaction = False

    def isInTransaction( self ) -> bool:
        return DatabaseConnection.inst().isInTransaction()

    def close( self ) -> None:
        self._con.close()

    def getDbName( self ) -> str:
        return DatabaseConnection.inst().getDbName()

    def getConnection( self ):
        return self._con.cursor()

    def readTable( self, table: str ) -> List[Dict]:
        sql = "select * from " + table
        dictList = self.readAllGetDict( sql )
        return dictList

    def getMaxId( self, table: str, id_name: str ) -> int:
        sql = "select max(%s) as max_id from %s" % (id_name, table)
        d = self.readOneGetDict( sql )
        return d["max_id"]

    def getWertebereiche( self, table:str=None, column:str=None ) -> List[XWertebereich]:
        """
        Liest alle Wertebereiche aus der Tabelle wertebereich
        :return:
        """
        sql = "select id, table_name, column_name, is_numeric, wert, beschreibung_kurz, beschreibung from wertebereich "
        if table:
            sql += "where table_name = '%s' and column_name = '%s' " % ( table, column )
        l: List[Dict] = self.readAllGetDict( sql )
        wbList: List[XWertebereich] = list()
        for d in l:
            x = XWertebereich( d )
            wbList.append( x )
        return wbList

    def getCurrentTimestamp( self ):
        return datetime.now().strftime( "%Y-%m-%d:%H.%M.%S" )

    def getIccTabellen( self ) -> List[str]:
        sql = "select name from sqlite_master where type = 'table' order by name"
        tupleList = self.read( sql )
        l = [x[0] for x in tupleList]
        return l

    def read( self, sql: str ) -> List[Tuple]:
        self._con.row_factory = None
        cur = self._con.cursor() # sieht umständlich aus, muss aber so gemacht werden:
                                 # mit jedem cursor()-call wird ein neuer Cursor erzeugt!
        cur.execute( sql )
        records = cur.fetchall()
        return records

    def dict_factory( self, cursor, row ):
        d = { }
        for idx, col in enumerate( cursor.description ):
            d[col[0]] = row[idx]
        return d

    def readOneGetDict( self, sql: str ) -> Dict or None:
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        return cur.fetchone()

    def readAllGetDict( self, sql: str ) -> List[Dict] or None:
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        return cur.fetchall()

    def readAllGetObjectList( self, sql, xbase:Type[XBase] ) -> List[XBase]:
        """
        :param sql:
        :param xbase: der gewünschte Rückgabetyp: eine von XBase abgeleitete Klasse
        :return: eine Liste von Objekten, die der gewünschten Klasse entsprechen - oder eine leere Liste
        """
        self._con.row_factory = self.dict_factory
        cur = self._con.cursor()
        cur.execute( sql )
        dictlist = cur.fetchall()
        retList = list()
        for d in dictlist:
            x = xbase( d )
            retList.append( x )
        return retList

    def write( self, sql: str ) -> int:
        c = self._con.cursor().execute( sql )
        if not self.isInTransaction():
            self._con.commit()
        return c.rowcount

def test():
    db = DatabaseCommon()
    sql = "select mv_id from mietverhaeltnis where mobj_id = 'bueb' and von <= CURRENT_DATE order by von desc"
    ret = db.read( sql )
    print( ret )
    ret = db.read( sql )
    print( ret )
    ret = db.read( sql )
    print( ret )
    # d = db.readOneGetDict( sql )
    # print( d )
