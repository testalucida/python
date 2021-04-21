from PySide2 import Qt
from PySide2.QtCore import *
from PySide2.QtGui import QFont, QBrush, QColor
import numbers
from typing import List, Dict, Any

from anlagev_interfaces import XAnlageV_Zeile

class AnlageVTableModel( QAbstractTableModel ):
    def __init__(self, zeileList:List[XAnlageV_Zeile]):
        QAbstractTableModel.__init__( self )
        self.zeilen:List[XAnlageV_Zeile] = zeileList
        self._rowCount = len( self.zeilen )
        if self._rowCount > 0:
            self._headers:List = list( self.zeilen[0].getHeaders() )
            self._columnCount = self.zeilen[0].getDisplayItemCount()
        else:
            self._headers:List = ["Keine Daten vorhanden"]
        self._negNumberBrush = QBrush( Qt.red )
        self._noneBrush = QBrush( Qt.lightGray )
        self._fonts:List[QFont] = None
        self._makeFonts()

        #self._changedCallback = None

    def _makeFonts( self ):
        self._fonts.append( QFont( "Arial", 11, QFont.Normal ) )
        self._fonts.append( QFont( "Arial", 11, QFont.Bold ) )
        self._fonts.append( QFont( "Arial", 12, QFont.Bold ) )

    # def setChangedCallback( self, callbackFnc ):
    #     self._changedCallback = callbackFnc

    # def doChangedCallback( self ):
    #     if self._changedCallback:
    #         self._changedCallback()

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return self._rowCount

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return self._columnCount

    def getValue(self, indexrow:int, indexcolumn:int ) -> Any:
        z = self.zeilen[indexrow]
        return z.getValue( indexcolumn )

    def getBackgroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        val = self.getValue( indexrow, indexcolumn )
        if val is None: return self._noneBrush
        else: return None

    def getForegroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        val = self.getValue( indexrow, indexcolumn )
        if isinstance(val, numbers.Number) and val < 0:
            return self._negNumberBrush
        else: return None

    def getFont(self, indexrow:int, indexcolumn:int ) -> QFont or None:
        z = self.zeilen[0]
        return self._fonts[z.fontFlag]

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
                if self.headerBrush:
                    return self.headerBrush
        return None

