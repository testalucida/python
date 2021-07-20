import copy
import numbers
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QBrush, QFont

import constants
from icctablemodel import IccTableModel
from interfaces import XRendite


class RenditeTableModel( IccTableModel ):
    def __init__( self, renditeList:List[XRendite] ):
        IccTableModel.__init__( self )
        self._renditeList:List[XRendite] = renditeList
        self._keyHeaderMapper = {
            "Objekt": "master_name",
            #"Wert": "wert",
            "qm": "qm",
            "Einnahmen": "einnahmen",
            "Ausgaben": "ausgaben",
            "davon Rep.": "davon_reparaturen",
            "Überschuss o.Afa": "ueberschuss_o_afa",
            "Ertrag je qm" : "ertrag_pro_qm",
            "AfA": "afa",
            "Überschuss m.Afa": "ueberschuss_m_afa"
        }
        self._headers = list( self._keyHeaderMapper.keys() )
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._objectColumnId = 0
        self._betragColumns = (1, 2, 3, 4, 5, 6, 7, 8)
        # self._sortable = False

    def getKeyList( self ) -> List[str]:
        return list( self._keyHeaderMapper.values() )

    def isChanged( self ) -> bool:
        return False

    # def setSortable( self, sortable:bool=True ):
    #     self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._renditeList )

    def getXRendite( self, row:int ) -> XRendite:
        return self._renditeList[row]

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self.getHeaders() )

    def isNumColumn( self, col: int ) -> bool:
        return True if col in self._betragColumns else False

    def getHeaders( self ) -> List[str]:
        return self._headers

    def getObjekt( self, row:int ):
       return self.getValue( row, self._objectColumnId )

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._renditeList[indexrow]
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
        #x = self.getXRendite( indexrow )
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

    def getRow( self, x: XRendite ) -> int:
        for r in range( len( self._renditeList ) ):
            e: XRendite = self._renditeList[r]
            if e == x:
                return r
        raise Exception( "RenditeTableModel.getRow(): can't find object '%s'" % ( x. master_name ) )

    def getListToSort( self ) -> List:
        return self._renditeList

    def receiveSortedList( self, li:List ) -> None:
        self._renditeList = li

    def compare( self, x1:XRendite, x2:XRendite ) -> int:
        key = self.getKeyList()[self.sort_col]
        v1 = x1.__dict__[key]
        v2 = x2.__dict__[key]
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return -1 if self.sort_reverse else 1
        if v1 > v2: return 1 if self.sort_reverse else -1
        if v1 == v2: return 0


if __name__ == "__main__":
    pass