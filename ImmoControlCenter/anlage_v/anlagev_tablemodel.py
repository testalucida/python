from PySide2 import Qt
from PySide2.QtCore import *
from PySide2.QtGui import QFont, QBrush, QColor
import numbers
from typing import List, Dict, Any

from anlagev_interfaces import XAnlageV_Zeile

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
    def __init__(self, zeilen:List[PreviewRow] ):
        QAbstractTableModel.__init__( self )
        self._rows = zeilen
        self._headers: List = ["Zeile", "Text", "Wert1", "Wert Anl.V VJ", "Details", "Bemerkung"]
        self._keys:List = ["zeile", "text", "wert1", "wert2", "detailLink", "bemerkung"]
        self._wertColumns:List = [2, 3]
        self._negNumberBrush = QBrush( Qt.red )
        self._separatorForeground = QBrush( Qt.white )
        self._noneBrush = QBrush( Qt.lightGray )
        color = QColor( 197, 217, 227 )
        self._fieldIdBrush = QBrush( color )
        self._separatorBrush = QBrush( Qt.darkGreen )
        self._normalFont = QFont( "Arial", 11, QFont.Normal )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._boldBigFont = QFont( "Arial", 12, QFont.Bold )

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
class Cell:
    def __init__(self, value:Any=None):
        self.value = value

class AnlageVTableModel__( QAbstractTableModel ):
    def __init__(self, zeileList:List[XAnlageV_Zeile]):
        QAbstractTableModel.__init__( self )
        self.zeilen:List[XAnlageV_Zeile] = zeileList
        self.table:List[List[Cell]] = list()
        self._rowCount = 0
        self._columnCount = 0

        if len( self.zeilen ) > 0:
            self._headers:List = list( self.zeilen[0].getHeaders() )
            self._provideRowAndColumnCount()
            self._createTableCells()
        else:
            self._headers:List = ["Keine Daten vorhanden"]
        self._negNumberBrush = QBrush( Qt.red )
        self._noneBrush = QBrush( Qt.lightGray )
        color = QColor( 197,217,227 )
        self._fieldIdBrush = QBrush( color )
        self._fonts:List[QFont] = list()
        self._makeFonts()

    def _provideRowAndColumnCount( self ):
        colsPerRow = 3  # zeilennr, feld_id, value
        fieldsInRow = 0
        maxfieldsInRow = 0
        rows = 0
        r = 0
        for z in self.zeilen:
            if r != z.nr:
                r = z.nr
                rows += 1
                if fieldsInRow > maxfieldsInRow:
                    maxfieldsInRow = fieldsInRow
                    fieldsInRow = 1
            else:
                fieldsInRow += 1

        self._rowCount = rows
        self._columnCount = 1 + (maxfieldsInRow-1) * 2 # zeilennummer + (max. Felder minus dem Feld für die Zeilennummer) * 2 => field_id, value

    def _createTableCells( self ):
        r = 0
        for z in self.zeilen:
            if r != z.nr:
                row = self._createRowForZeilennummer( z.nr )
                self.table.append( row )
                self._provideValuesForRow( row, z.feld_id, z.value )
                r = z.nr
            else:
                self._provideValuesForRow( row, z.feld_id, z.value )

    def _createRowForZeilennummer( self, znr:int ) -> List[Cell]:
        row:List[Cell] = list()
        for c in range( self._columnCount ):
            row.append( Cell() )
        row[0].value = znr
        return row

    def _provideValuesForRow( self, row:List[Cell], field_id, value ):
        for c in range( self._columnCount ):
            if row[c].value is None:
                row[c].value = field_id
                row[c+1].value = " " if value is None else value
                return

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
        # z = self.zeilen[indexrow]
        # return z.getValue( indexcolumn )
        cell = self.table[indexrow][indexcolumn]
        return cell.value

    def getBackgroundBrush(self, indexrow:int, indexcolumn:int ) -> QBrush or None:
        if indexcolumn == 1: return self._fieldIdBrush
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
                pass
                # if self.headerBrush:
                #     return self.headerBrush
        return None

