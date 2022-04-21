from typing import List

from anleihen.anleihedatareader import getAllDKBAnleihen
from interface.interfaces import PopoTable


class AnleiheLogic:
    def __init__( self ):
        pass

    def getAnleihenData( self ) -> List[PopoTable]:
        """
        Provides a list of PopoTables each containing all anleihen on a particular day
        :return:
        """
        popotableList = getAllDKBAnleihen()