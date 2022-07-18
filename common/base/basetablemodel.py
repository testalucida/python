import decimal
import numbers
from functools import cmp_to_key
from PySide2.QtCore import QAbstractTableModel, SIGNAL, Qt, QModelIndex, QSize
from typing import Any, List, Dict, Tuple, Iterator
from PySide2.QtGui import QColor, QBrush, QFont, QPixmap

from base.interfaces import XBase
from base.change import ChangeLog

##################  KeyHeaderMapping  ################
class KeyHeaderMapping:
    def __init__( self, key=None, header=None ):
        self.key = key
        self.header = header

##################  BaseTableModel  ##################
class BaseTableModel( QAbstractTableModel ):
    def __init__( self, rowList:List[XBase]=None, jahr:int=None ):
        QAbstractTableModel.__init__( self )
        self.rowList:List[XBase] = rowList
        self._jahr:int = jahr # das Jahr ist bei manchen Models interessant, bei manchen nicht - kann also auf None stehen.
        self.headers:List = list()
        self.keys:List = list()
        self.headerColor = QColor( "#FDBC6A" )
        self.headerBrush = QBrush( self.headerColor )
        self.negNumberBrush = QBrush( Qt.red )
        self.greyBrush = QBrush( Qt.lightGray )
        self.inactiveBrush = QBrush( Qt.black )
        self.inactiveBrush.setStyle( Qt.BDiagPattern )
        self.boldFont = QFont( "Arial", 11, QFont.Bold )
        self.yellow = QColor( "yellow" )
        self.yellowBrush = QBrush( self.yellow )
        self.sortable = False
        self.sort_col = 0
        self.sort_ascending = False
        self._changes = ChangeLog()
        if rowList:
            self.setRowList( rowList )

    def _setDefaultKeyHeaderMapping( self ):
        """
        Per default verwenden wir die Keys eines der übergebenen Dictionaries als Keys und Headers
        :return:
        """
        XBase = self.rowList[0]
        for k in XBase.getKeys():
            self.keys.append( k )
            self.headers.append( k )

    def setRowList( self, rowList:List[XBase] ):
        self.rowList = rowList
        if len( rowList ) > 0:
            self._setDefaultKeyHeaderMapping()

    def receiveSortedList( self, li:List[XBase] ) -> None:
        self.rowList = li

    def setKeyHeaderMappings( self, mappings:List[KeyHeaderMapping] ):
        self.headers = [x.header for x in mappings]
        self.keys = [x.key for x in mappings]

    def getColumnIndex( self, header ) -> int:
        return self.headers.index( header )

    def getHeaders( self ) -> List[str]:
        return self.headers

    def getHeader( self, col:int ) -> Any:
        return self.headerData( col, orientation=Qt.Horizontal, role=Qt.DisplayRole )

    def getKeyByHeader( self, header:Any ) -> Any:
        headerIndex = self.headers.index( header )
        return self.keys[headerIndex]

    def getRowList( self ) -> List[XBase]:
        """
        :return: die rohe Liste der XBase-Elemente
        """
        return self.rowList

    def getJahr( self ) -> int:
        return self._jahr

    def getRow( self, x:XBase ) -> int:
        """
        Liefert die Zeile, in der das spezifizierte XBase-Objekt dargestellt wird
        :param x:
        :return:
        """
        return self.rowList.index( x )

    def getElement( self, indexrow: int ) -> XBase:
        return self.rowList[indexrow]

    def getKey( self, indexcolumn:int ):
        return self.keys[indexcolumn]

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        e:XBase = self.getElement( indexrow )
        return e.getValue( self.keys[indexcolumn] )

    def getValueByName( self, indexrow:int, attrName:str ) -> Any:
        e:XBase = self.getElement( indexrow )
        return e.getValue( attrName )

    def setValue( self, indexrow:int, indexcolumn:int, value:Any, writeChangeLog:bool=True ) -> None:
        """
        Ändert einen Wert in dem durch indexrow spezifiz. XBase-Element und
        schreibt das Change-Log
        Löst *kein* dataChanged-Signal aus.
        Um ein dataChanged-Signal auszulösen, muss die setData-Methode verwendet werden.
        :param indexrow:
        :param indexcolumn:
        :param value:
        :return:
        """
        oldval = self.getValue( indexrow, indexcolumn )
        if oldval == value: return
        e:XBase = self.getElement( indexrow )
        key = self.keys[indexcolumn]
        e.setValue( key, value )
        if writeChangeLog:
            self.addChange( e, key, oldval, value )

    def addChange( self, e:XBase, key, oldval, value ):
        self._changes.addChange( e, key, oldval, value )

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self.rowList )

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return len( self.headers )

    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            v = self.getValue( index.row(), index.column() )
            if isinstance( v, numbers.Number ): return int( Qt.AlignRight | Qt.AlignVCenter )
        elif role == Qt.BackgroundRole:
            return self.getBackgroundBrush( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForegroundBrush( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self.getFont( index.row(), index.column() )
        elif role == Qt.DecorationRole:
            return self.getDecoration( index.row(), index.column() )
        elif role == Qt.SizeHintRole:
            return self.getSizeHint( index.row(), index.column() )
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.headers[col]
            if role == Qt.BackgroundRole:
                if self.headerBrush:
                    return self.headerBrush
        return None

    def getBackgroundBrush( self, indexrow: int, indexcolumn: int ) -> QBrush or None:
        return None

    def getForegroundBrush( self, indexrow: int, indexcolumn: int ) -> QBrush or None:
        if self.negNumberBrush:
            val = self.getValue( indexrow, indexcolumn )
            if isinstance( val, numbers.Number ) and val < 0:
                return QBrush( Qt.red )

    def getFont( self, indexrow: int, indexcolumn: int ) -> QFont or None:
        return None

    def getDecoration( self, indexrow: int, indexcolumn: int ) -> QPixmap or None:
        return None

    def getSizeHint( self, indexrow:int, indexcolumn:int ) -> QSize or None :
        return None

    def setHeaderColor( self, color:QColor ):
        self.headerColor = color

    def displayNegNumbersRed( self, on:bool=False ):
        if on:
            self.negNumberBrush = QBrush( Qt.red )
        else:
            self.negNumberBrush = None

    # def find( self, value, caseSensitive:bool=False, exactMatch:bool=False ):
    #     """
    #     Sucht nach Vorkommen von <value> in allen Spalten und Zeilen und liefert
    #     die Position eines jeden Treffers als row/column-Tuple zurück.
    #     Die Suche erfolgt sowohl auf String-Basis wie auch auf numerischer Basis, wenn der
    #     Suchbegriff in eine Zahl (int oder float) umgewandelt werden kann.
    #     Als Treffer gilt auch, wenn <exactMatch> == False und der Suchbegriff <value> nur ein Teilstring
    #     eines Wertes aus dem TableModel ist.
    #     :param value: Suchbegriff, numerisch oder alpha
    #     :param caseSensitive: ob Groß-/Kleinschreibung beachtet werden soll
    #     :param exactMatch: ob der Vergleich zwischen den kompletten Strings erfolgen soll oder ob als Match auch
    #                     gelten soll, wenn <value> ein Teilstring des TableModel-Wertes ist.
    #     :return: yields jeden Treffer bestehend aus einem Tuple(row-Index, column-Index)
    #     """
    #     def makeComparable( val ):
    #         valNum = None
    #         if type( val ) in (int, float):
    #             valNum = val
    #             val = str( val )
    #         else: # string (hopefully)
    #             try:
    #                 valNum = int(val)
    #             except ValueError:
    #                 try:
    #                     valNum = float(val)
    #                 except ValueError:
    #                     pass
    #         if not caseSensitive:
    #             val = val.lower()
    #         return val, valNum
    #
    #     value, valueNum = makeComparable( value )
    #     l: List[Tuple] = list()
    #     for r in range( 0, self.rowCount() ):
    #         for c in range( 0, self.columnCount() ):
    #             tmval = self.getValue( r, c )
    #             tmval, tmvalNum = makeComparable( tmval )
    #             match = False
    #             if (exactMatch and value == tmval) or (not exactMatch and value in tmval ):
    #                 match = True
    #             if match or (tmvalNum is not None and valueNum is not None and tmvalNum == valueNum):
    #                 #l.append( (r, c) )
    #                 yield r, c
    #     #return l

    def isChanged( self ) -> bool:
        return self._changes.hasChanges()

    def getChanges( self ) -> ChangeLog:
        return self._changes

    def clearChanges( self ):
        self._changes.clear()

    def setSortable( self, sortable:bool=True ):
        self.sortable = sortable

    def sort( self, col:int, order: Qt.SortOrder ) -> None:
        if not self.sortable: return
        """sort table by given column number col"""
        self.layoutAboutToBeChanged.emit()
        self.sort_col = col
        self.sort_ascending = True if order == Qt.SortOrder.AscendingOrder else False
        self.rowList = sorted( self.rowList, key=cmp_to_key( self.compare ) )
        self.layoutChanged.emit()

    def compare( self, x1:XBase, x2:XBase ) -> int:
        key = self.getKey( self.sort_col )
        v1 = x1.getValue( key )
        v2 = x2.getValue( key )
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return 1 if self.sort_ascending else -1
        if v1 > v2: return -1 if self.sort_ascending else 1
        if v1 == v2: return 0