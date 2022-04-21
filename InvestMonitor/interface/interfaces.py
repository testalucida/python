import datetime
from typing import List, Tuple, Any

import numpy


class PortfolioPosition:
    def __init__( self ):
        self.isin = ""
        self.bezeichnung = ""
        self.nennwert = 0
        self.kurs = 0.0
        self.kurswert = 0.0

    def toString(self) -> str:
        return self.isin + "\t" + self.bezeichnung + "\t" + str( self.kurs ) + "\t" + str( self.kurswert )


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

class Kurs:
    def __init__( self ):
        self.tag = ""
        self.kurs_prozent = 0.0
        self.kurswert = 0.0
        self.gewinn_verlust = 0.0

class Anleihe:
    def __init__( self, bezeichnung:str, isin:str, nennwert:int, kurse:List[Kurs], color:str ):
        """
        Data needed for displaying this Anleihe.
        :param emittent: e.g. Post
        :param isin:
        :param nennwert: e.g. 300000
        :param kurse: e.g. [101.3, 100.6, 99.4, 108.9]
        :param color: one of {'r': red, 'g': green, 'b': blue, 'c': cyan, 'y': mud}
        """
        self.bezeichnung = bezeichnung
        self.isin = isin
        self.nennwert = nennwert
        self.kurse:List[Kurs] = kurse
        self.color = color

class Point:
    def __init__( self, x:Any, y:Any ):
        self.x = x
        self.y = y

class Path:
    def __init__( self, id:str = "" ):
        self._id = id
        self._points:List[Point] = []
        self._color = ""
        self._legend = ""

    def setId( self, id:str ):
        self._id = id

    def getId( self ) -> str:
        return self._id

    def setLegend( self, legend:str ):
        self._legend = legend

    def getLegend( self ) -> str:
        return self._legend

    def addPoint( self, point:Point ) -> None:
        self._points.append( point )

    def getPoints( self ) -> List[Point]:
        return self._points

    def setColor( self, color:str ):
        self._color = color

    def getColor( self ) -> str:
        return self._color

    def getXvalues( self ) -> List[float]:
        return [p.x for p in self._points]

    def getYvalues( self ) -> List[float]:
        return [p.y for p in self._points]

class GraphData:
    """
    Base class for drawing paths using GraphCreator
    """
    def __init__( self ):
        """
        class provides data for drawing the performance line of one or more shares
        Each performance linee is represented by a Path object
        """
        self._title = ""
        self._ylabel = ""
        self._xlabel = ""
        self._paths:List[Path] = []

    def addPath( self, path:Path ):
        self._paths.append( path )

    def setTitle( self, title:str ):
        self._title = title

    def getTitle( self ):
        return self._title

    def setXlabel( self, label:str ):
        self._xlabel = label

    def getXlabel( self ):
        """
        label to be displayed beneath x-axis
        :return:
        """
        return self._xlabel

    def setYlabel( self, label:str ):
        self._ylabel = label

    def getYlabel( self ):
        """
        label to be displayed besides y-axis
        :return:
        """
        return self._ylabel

    def getPaths( self ) -> List[Path]:
        return self._paths

    def getPathById( self, pathId:str ) -> Path or None:
        for path in self._paths:
            if path.getId() == pathId:
                return path
        return None


class DateBasedGraphData( GraphData ):
    def __init__( self, dates:List[datetime.datetime] ):
        """
         :param dates: date values as units for x-axis
        :param dates:
        """
        GraphData.__init__( self )
        self._dates = dates

    #def getXvalues( self ) -> :



