from typing import List, Tuple


class PortfolioPosition:
    def __init__( self ):
        self.isin = ""
        self.bezeichnung = ""
        self.kurs = 0.0

    def toString(self) -> str:
        return self.isin + "\t" + self.bezeichnung + "\t" + str( self.kurs )


class PopoTable:
    """
    Eine PopoTable enthält die Positionen (Anleihen) des DKB-Depots zu *einem* Zeitpunkt
    """
    def __init__( self, snapshot:str ):
        self.header = "ISIN\tBezeichnung\t\tKurs" #no function
        self._snapshot = snapshot
        self._isoDate:str = ""
        self._time:str = ""
        self.popoList:List[PortfolioPosition] = list()
        self._splitSnapshot( snapshot )

    def _splitSnapshot( self, snapshot:str ):
        sep = snapshot.rfind( " " )
        day = snapshot[:sep]
        self._time = snapshot[sep + 1:]
        d = day[:2]
        m = day[3:5]
        y = day[6:10]
        self._isoDate = y + "-" + m + "-" + d

    def addPopo( self, popo:PortfolioPosition ):
        self.popoList.append( popo )

    def getSnapshot( self ) -> str:
        return self._snapshot

    def getSnapshotDate( self ) -> str:
        """
        returns date part of snapshot in iso format
        :return:
        """
        return self._isoDate

    def getSnapshotTime( self ) -> str:
        """
        returns time part of snapshot
        :return:
        """
        return self._time

    def print( self ):
        print( "PopoTable vom %s:" % ( self.getSnapshot() ) )
        for popo in self.popoList:
            print( popo.toString() )