from PySide2 import Qt
from PySide2.QtCore import *
from PySide2.QtGui import QFont, QBrush, QColor
import numbers
from typing import List, Dict, Any

class PreviewRow:
    def __init__(self):
        self.zeile:Any = None
        self.text:str = ""
        self.wert1:Any = None
        self.wert2:Any = None
        self.detailLink:str = ""
        self.bemerkung:str = ""
        self.isSeparator:bool = False
        self.isSumme:bool = False

class AnlageVTableModel( QAbstractTableModel ):
    def __init__(self, master_name:str, jahr:int, zeilen:List[PreviewRow] ):
        QAbstractTableModel.__init__( self )
        self._master_name = master_name
        self._jahr = jahr
        self._rows = zeilen
        self._headers: List = ["Zeile", "Text", "Wert1", "Wert Anl.V VJ", "Details", "Bemerkung"]
        self._keys:List = ["zeile", "text", "wert1", "wert2", "detailLink", "bemerkung"]
        self._wertColumns:List = [2, 3]
        self._detailLinkColumn = 4
        self._negNumberBrush = QBrush( Qt.red )
        self._separatorForeground = QBrush( Qt.white )
        self._noneBrush = QBrush( Qt.lightGray )
        color = QColor( 197, 217, 227 )
        self._fieldIdBrush = QBrush( color )
        self._separatorBrush = QBrush( Qt.darkGreen )
        self._normalFont = QFont( "Arial", 11, QFont.Normal )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._boldBigFont = QFont( "Arial", 12, QFont.Bold )

    def getMasterName( self ) -> str:
        return self._master_name

    def getJahr( self ) -> int:
        return self._jahr

    def getDetailLinkColumnIndex( self ):
        return self._detailLinkColumn

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._rows )

    def columnCount( self, parent:QModelIndex=None ) -> int:
        return len( self._headers )

    def getValue(self, indexrow:int, indexcolumn:int ) -> Any:
        row = self.getPreviewRow( indexrow )
        return self.getValue2( row, indexcolumn )

    def getValue2( self, row:PreviewRow, indexcolumn:int ) -> Any:
        return row.__dict__[self._keys[indexcolumn]]

    def getPreviewRow( self, indexrow:int ) -> PreviewRow:
        return self._rows[indexrow]

    def getBackgroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        row = self.getPreviewRow( indexrow )
        if row.isSeparator:
            if row.text:
                return self._separatorBrush
            else:
                return self._noneBrush
        if indexcolumn == 1:
            return self._fieldIdBrush
        val = self.getValue2( row, indexcolumn )
        if val is None: return self._noneBrush
        else: return None

    def getForegroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        row = self.getPreviewRow( indexrow )
        if row.isSeparator:
            return self._separatorForeground
        val = self.getValue2( row, indexcolumn )
        if isinstance(val, numbers.Number) and val < 0:
            return self._negNumberBrush
        else: return None

    def getFont(self, indexrow:int, indexcolumn:int ) -> QFont or None:
        row = self.getPreviewRow( indexrow )
        # if row.text.startswith( "Hausgeld" ):
        #     print( "JJ")
        if row.isSeparator:
            return self._boldFont
        if row.zeile:
            if indexcolumn in ( self._wertColumns ) \
            and ( row.wert1 or row.wert2 ):
                if row.isSumme:
                    return self._boldBigFont
                else:
                    return self._boldFont
            elif row.isSumme:
                return self._boldFont
        return self._normalFont

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
                pass
                # if self.headerBrush:
                #     return self.headerBrush
        return None


##########################################################################################
