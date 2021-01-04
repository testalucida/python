from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt

import constants
from icctablemodel import IccTableModel
from interfaces import XSollzahlung

class SollzahlungenTableModel( IccTableModel ):
    def __init__( self, sollList:List[XSollzahlung] ):
        IccTableModel.__init__( self )
        self.sollList:List[XSollzahlung] = sollList
        """
        Gewünschte Spaltenfolge: 
        Objekt | Mieter / WEG | von | bis | netto | NKV / RüZuFü | Bemerkung
        """

        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XSollzahlung]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "INSERT": List[XSollzahlung],
            "UPDATE": List[XSollzahlung],
            "DELETE": List[XSollzahlung]
        }
        """
        self._sortable = False

    def setSortable( self, sortable:bool=True ):
        self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self.sollList )

    @abstractmethod
    def columnCount( self, parent:QModelIndex=None ) -> int:
       pass

    def getXSollzahlung( self, row:int ) -> XSollzahlung:
        return self.sollList[row]

    @abstractmethod
    def getKeyList( self ) -> List[str]:
        pass

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self.getHeaders() )

    @abstractmethod
    def isNumColumn( self, col: int ) -> bool:
        pass

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self.sollList[indexrow]
        key = self.getKeyList()[indexcolumn]
        val = x.__dict__[key]
        return val

    def getAlignment( self, indexrow: int, indexcolumn: int ):
        if self.isNumColumn( indexcolumn ):
            return int( Qt.AlignRight | Qt.AlignVCenter )
        else:
            return int( Qt.AlignLeft | Qt.AlignVCenter )

    def data( self, index: QModelIndex, role: int = None ):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self.getValue( index.row(), index.column() )
        elif role == Qt.TextAlignmentRole:
            return self.getAlignment( index.row(), index.column() )
        # elif role == Qt.ForegroundRole:
        #     return self.getForeground( index.row(), index.column() )
        # elif role == Qt.FontRole:
        #     return self.getFont( index.row(), index.column() )
        return None

    def headerData( self, col, orientation, role=None ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.getHeaders()[col]
            # if role == Qt.BackgroundRole:
            #     pass
        return None

################################################################
class SollmietenTableModel( SollzahlungenTableModel ):
    def __init__( self, sollList: List[XSollzahlung] ):
        SollzahlungenTableModel.__init__( self, sollList )
        self._numColumns: Tuple = (4, 5, 6)

    def isNumColumn( self, col:int ) -> bool:
        return col in self._numColumns

    def getKeyList( self ) -> Tuple[str]:
        return ( "mobj_id", "mv_id", "von", "bis", "netto", "nkv", "bemerkung" )

    def getHeaders( self ) -> Tuple[str]:
        return ( "Objekt", "Mieter", "von", "bis", "netto", "NKV", "Bemerkung" )

#################################################################
class SollHGVTableModel( SollzahlungenTableModel ):
    def __init__( self, sollList: List[XSollzahlung] ):
        SollzahlungenTableModel.__init__( self, sollList )
        self._numColumns:Tuple = (4, 5, 6)

    def isNumColumn( self, col:int ) -> bool:
        return col in self._numColumns

    def getKeyList( self ) -> List[str]:
        return ( "mobj_id", "weg_name", "von", "bis", "netto", "ruezufue", "brutto", "bemerkung" )

    def getHeaders( self ) -> List[str]:
        return ( "Objekt", "WEG", "von", "bis", "netto", "RüZuFü", "Brutto", "Bemerkung" )


if __name__ == "__main__":
    x = XSollzahlung()
    l = [x,]
    m = SollzahlungenTableModel( l )
    m2 = SollmietenTableModel( l )