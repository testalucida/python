import sqlite3
from sqlite3 import Connection

class ConnectionProvider:
    __instance = None

    def __init__( self ):
        self._connection:Connection = None
        if ConnectionProvider.__instance != None:
            raise Exception( "You can't instantiate ConnectionProvider more than once." )
        else:
            ConnectionProvider.__instance = self
            try:
                self._connection = sqlite3.connect( "../immo.db" )
            except Exception as ex:
                print( str( ex ) )

    @staticmethod
    def inst() -> __instance:
        if ConnectionProvider.__instance == None:
            ConnectionProvider()
        return ConnectionProvider.__instance

    def getConnection( self ) -> Connection:
        return self._connection