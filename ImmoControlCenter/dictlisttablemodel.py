from PySide2 import Qt
from PySide2.QtCore import *
from PySide2.QtGui import QFont, QBrush, QColor
import numbers
from typing import List, Dict, Any

class DictListTableModel( QAbstractTableModel ):
    def __init__(self, dictList:List[Dict]):
        QAbstractTableModel.__init__( self )
        self._rowlist:List[Dict] = dictList
        if len( self._rowlist ) > 0:
            self._headers:List = list( self._rowlist[0].keys() )
        else:
            self._headers:List = ["Keine Daten vorhanden"]
        self._headerBrush:QBrush = None
        self._negNumberBrush = None

    def rowCount( self, parent:QModelIndex ) -> int:
        return len(self._rowlist)

    def columnCount(self, parent:QModelIndex) -> int:
        if len( self._rowlist ) == 0: return 0
        return len(self._rowlist[0])

    def updateValue( self, index:QModelIndex, value:Any ):
        self.updateValue2( index.row(), index.column(), value )
        return True

    def updateValue2(self, row:int, col:int, value:Any ):
        rowdict = self._rowlist[row]
        key = self._headers[col]
        rowdict[key] = value
        index = self.createIndex( row, col )
        self.dataChanged.emit(index, index)
        return True

    def setHeaderColor(self, color:QColor ) -> None:
        self._headerBrush = QBrush( color )

    def getValue(self, indexrow:int, indexcolumn:int ) -> Any:
        key = self._headers[indexcolumn]
        d: Dict = self._rowlist[indexrow]
        return d[key]

    def displayNegNumbersRed( self, on:bool=False ):
        if on:
            self._negNumberBrush = QBrush( Qt.red )
        else:
            self._negNumberBrush = None

    def getBackgroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        return None

    def getForegroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        if self._negNumberBrush:
            val = self.getValue( indexrow, indexcolumn )
            if isinstance(val, numbers.Number) and val < 0:
                return QBrush( Qt.red )

    def getFont(self, indexrow:int, indexcolumn:int ) -> QFont or None:
        return None

    def data(self, index: QModelIndex, role: int = None):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
             v = self.getValue( index.row(), index.column() )
             if isinstance( v, numbers.Number ): return int(Qt.AlignRight | Qt.AlignVCenter)
        elif role == Qt.BackgroundRole:
            return self.getBackgroundBrush( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForegroundBrush( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self.getFont( index.row(), index.column() )
        return None

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self._headers[col]
            if role == Qt.BackgroundRole:
                if self._headerBrush:
                    return self._headerBrush
        return None

    def sort( self, col:int, order: Qt.SortOrder ) -> None:
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        sort_reverse = True if order == Qt.SortOrder.AscendingOrder else False
        self._rowlist = sorted(self._rowlist, key=lambda x: x[self._headers[col]], reverse=sort_reverse )
        self.emit(SIGNAL("layoutChanged()"))

