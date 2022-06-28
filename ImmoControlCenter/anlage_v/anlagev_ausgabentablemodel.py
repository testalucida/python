import numbers
from typing import List, Any, Callable
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QFont, QBrush

from anlage_v.anlagev_interfaces import XAusgabeKurz
from interfaces import XSonstAus

class ColumnFunction:
    def __init__(self):
        self.triggerColumn:int = -1
        self.fnc = None
        self.arg = None

class AnlageV_AusgabenTableModel( QAbstractTableModel ):
    def __init__( self, master_name:str, jahr:int, rowList: List[Any] ):
        QAbstractTableModel.__init__( self )
        self._master_name = master_name
        self._jahr = jahr
        self._rowList = rowList
        self._headers:List[str] = ["Kreditor", "Wohng", "Buchungstext", "Buch.datum", "Kostenart", "Betrag", "Summe"]
        self._keys:List[str] = ["kreditor", "mobj_id", "buchungstext", "buchungsdatum", "kostenart", "betrag", ""]
        self._columnKreditor = 0
        self._columnBetrag = 5
        self._columnSumme = 6
        self._negNumberBrush = QBrush( Qt.red )
        self._sumrowBrush = QBrush( Qt.lightGray )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._columnfunctions:List[ColumnFunction] = list()

    def addColumnFunction( self, triggercolumn:int, fnc, arg ):
        cf = ColumnFunction()
        cf.triggerColumn = triggercolumn
        cf.fnc = fnc
        cf.arg = arg
        self._columnfunctions.append( cf )

    def _getColumnFunction( self, column:int ) -> ColumnFunction or None:
        #l = [x.fnc for x in self._columnfunctions if x.column == column]
        #return l
        l = [cf for cf in self._columnfunctions if cf.triggerColumn == column]
        return l[0]

    def getMasterName( self ) -> str:
        return self._master_name

    def rowCount( self, parent: QModelIndex = None ) -> int:
        return len( self._rowList ) + 1 # +1 wegen der Summenzeile

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self._headers )

    def _getForegroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        val = self.getValue( indexrow, indexcolumn )
        if isinstance(val, numbers.Number) and val < 0:
            return self._negNumberBrush
        else: return None

    def _getBackgroundBrush( self, indexrow: int, indexcolumn: int ) -> QBrush or None:
        if indexrow == len( self._rowList ):
            return self._sumrowBrush

    def _getFont( self, indexrow: int, indexcolumn: int ) -> QFont or None:
        if indexrow == len( self._rowList ):
            if indexcolumn == 0 or self._keys[indexcolumn] == "":
                return self._boldFont
        return None

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexrow >= self.rowCount(): return None
        if indexrow == self.rowCount() - 1: # Summenzeile ausgeben
            if indexcolumn == 0:
                return "SUMME über Alle"
            elif self._keys[indexcolumn] == "":
                return sum( x.betrag for x in self._rowList )
            else:
                return ""
        else:
            x = self._rowList[indexrow]
            key = self._keys[indexcolumn]
            if key == "":
                # fnc = self._getColumnFunction( indexcolumn )
                # if fnc:
                #     return fnc( self, indexrow, indexcolumn )
                colfnc = self._getColumnFunction( indexcolumn )
                if colfnc:
                    return colfnc.fnc( self, indexrow, indexcolumn, colfnc.arg )
            val = x.__dict__[key]
            return val

    # def _getKreditorSumme( self, indexrow:int ) -> float or None:
    #     """
    #     Prüfen, ob ein Gruppenwechsel bezüglich Kreditor bevorsteht.
    #     Wenn ja, Summe des vorausgehenden Kreditors berechnen.
    #     Wenn nein, nichts zurückgeben.
    #     :param indexrow:
    #     :return:
    #     """
    #     thisKreditor = self.getValue( indexrow, self._columnKreditor )
    #     nextKreditor = self.getValue( indexrow + 1, self._columnKreditor )
    #     if nextKreditor is None or nextKreditor != thisKreditor:
    #         sum = 0
    #         startrow = self._getStartRow( thisKreditor, indexrow )
    #         for r in range( startrow, indexrow + 1 ):
    #             sum += self.getValue( r, self._columnBetrag )
    #         return sum
    #     return None

    def getStartRow( self, cmp:Any, endrow:int, cmpcol:int ) -> int:
        for r in range( endrow, -1, -1 ):
            #print( "_getStartRow(): range rückwärts von endrow %d bis 0: r = %d" % (endrow, r))
            tmp = self.getValue( r, cmpcol )
            if tmp != cmp:
                return r + 1
        return 0

    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            v = self.getValue( index.row(), index.column() )
            if isinstance( v, numbers.Number ): return int( Qt.AlignRight | Qt.AlignVCenter )
        elif role == Qt.ForegroundRole:
            return self._getForegroundBrush( index.row(), index.column() )
        elif role == Qt.BackgroundRole:
            return self._getBackgroundBrush( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self._getFont( index.row(), index.column() )
        return None

    def setHeaders( self, headers:List[str] ):
        self._headers = headers

    def setKeys( self, keys:List[str] ):
        self._keys = keys

    def headerData( self, col, orientation, role=None ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
            if role == Qt.BackgroundRole:
                pass
                # if self.headerBrush:
                #     return self.headerBrush
        return None