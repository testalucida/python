from typing import List, Any
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QBrush, QFont
from icc.icctablemodel import IccTableModel
from interfaces import XZahlung3


class Rendite_ZahlungenTableModel( IccTableModel ):
    def __init__( self, zahlungList:List[XZahlung3] ):
        IccTableModel.__init__( self )
        self._zahlungList:List[XZahlung3] = zahlungList
        self._keyHeaderMapper = {
            "Art": "art",
            "Objekt": "mobj_id",
            "Kreditor": "kreditor",
            "Betrag": "betrag",
            "Buchungsdatum": "buchungsdatum",
            "Buchungstext": "buchungstext",
        }
        self._headers = list( self._keyHeaderMapper.keys() )
        self._greyBrush = QBrush( Qt.gray )
        self._lightgreyBrush = QBrush( Qt.lightGray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._kostenartColumnId = 0
        self._objectColumnId = 1
        self._betragColumns = ( 3, )
        # self._sortable = False

    def isChanged( self ) -> bool:
        return False

    # def setSortable( self, sortable:bool=True ):
    #     self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._zahlungList )

    def getXZahlung3( self, row:int ) -> XZahlung3:
        return self._zahlungList[row]

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self.getHeaders() )

    def isNumColumn( self, col: int ) -> bool:
        return True if col in self._betragColumns else False

    def getHeaders( self ) -> List[str]:
        return self._headers

    def getObjekt( self, row:int ):
       return self.getValue( row, self._objectColumnId )

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._zahlungList[indexrow]
        header = self._headers[indexcolumn]
        key = self._keyHeaderMapper.get( header )
        val = x.__dict__[key]
        if indexcolumn in self._betragColumns:
            val = float( val )
        return val

    def getAlignment( self, indexrow: int, indexcolumn: int ):
        if self.isNumColumn( indexcolumn ):
            return int( Qt.AlignRight | Qt.AlignVCenter )
        else:
            return int( Qt.AlignLeft | Qt.AlignVCenter )

    def getForeground( self, indexrow:int, indexcolumn: int ) -> Any:
        if indexcolumn in self._betragColumns:
            val = self.getValue( indexrow, indexcolumn )
            if val < 0:
                return self._redBrush
        return None

    def getFont( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexcolumn in self._betragColumns:
            return self._boldFont

    def getBackground( self, indexrow: int, indexcolumn: int ) -> Any:
        val = self.getValue( indexrow, self._kostenartColumnId )
        if val == "":
            return self._lightgreyBrush
        return None

    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            return self.getAlignment( index.row(), index.column() )
        elif role == Qt.ForegroundRole:
            return self.getForeground( index.row(), index.column() )
        elif role == Qt.FontRole:
            return self.getFont( index.row(), index.column() )
        elif role == Qt.BackgroundRole:
            return self.getBackground( index.row(), index.column() )
        return None

    def headerData( self, col, orientation, role=None ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.getHeaders()[col]
            # if role == Qt.BackgroundRole:
            #     pass
        return None

    def getRow( self, x: XZahlung3 ) -> int:
        for r in range( len( self._zahlungList ) ):
            e: XZahlung3 = self._zahlungList[r]
            if e == x:
                return r
        raise Exception( "Rendite_ZahlungenTableModel.getRow(): can't find object '%s'" % ( x. master_name ) )

    def getListToSort( self ) -> List:
        return self._zahlungList

    def receiveSortedList( self, li:List ) -> None:
        self._zahlungList = li

    def compare( self, x1:Any, x2:Any ) -> int:
        key = self.getKeyList()[self._sort_col]
        v1 = x1.__dict__[key]
        v2 = x2.__dict__[key]
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return -1 if self._sort_reverse else 1
        if v1 > v2: return 1 if self._sort_reverse else -1
        if v1 == v2: return 0


if __name__ == "__main__":
    pass