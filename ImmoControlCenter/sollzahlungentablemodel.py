from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QBrush, QFont

import constants
from icctablemodel import IccTableModel
from interfaces import XSollzahlung, XSollHausgeld, XSollMiete


class SollzahlungenTableModel( IccTableModel ):
    def __init__( self, sollList:List[XSollzahlung] ):
        IccTableModel.__init__( self )
        self.sollList:List[XSollzahlung] = sollList

        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XSollzahlung]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "INSERT": List[XSollzahlung],
            "UPDATE": List[XSollzahlung],
        }
        """
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._objektColumn = 0
        self._vonbisColumns = (2, 3)
        self._betragColumns = (4, 5, 6)
        self._bruttoColumn = 6
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

    @abstractmethod
    def getHeaders( self ) -> Tuple[str]:
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

    def getForeground( self, indexrow:int, indexcolumn: int ) -> Any:
        if indexcolumn == self._objektColumn:
            return self._greyBrush
        elif indexcolumn in self._vonbisColumns:
            return self._greyBrush
        elif indexcolumn in self._betragColumns:
            val = self.getValue( indexrow, indexcolumn )
            if val < 0:
                return self._redBrush
        return None

    def getFont( self, indexrow: int, indexcolumn: int ) -> Any:
        if indexcolumn == self._bruttoColumn:
            return self._boldFont

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
        return None

    def headerData( self, col, orientation, role=None ):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.getHeaders()[col]
            # if role == Qt.BackgroundRole:
            #     pass
        return None

    def update( self, x:XSollzahlung ):
        row = self.getRow( x )
        cols = len( self.getHeaders() )
        idxfrom = self.index( row, 0 )
        idxbis = self.index( row, cols - 1 )
        self.writeChangeLog( constants.tableAction.UPDATE, x )
        self.dataChanged.emit( idxfrom, idxbis )

    def resetChanges( self ):
        for k in self._changes.keys():
            self._changes[k] = list()

    @abstractmethod
    def getRow( self, x: XSollzahlung ) -> int:
        pass

    #@abstractmethod
    def writeChangeLog( self, actionId:constants.tableAction, x:XSollzahlung ):
        """
        Schreibt ein in-memory-Log der eingefügten, geänderten, gelöschten Zahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist: List[XSollzahlung] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

    def getChanges( self ) -> Dict[str, List[XSollzahlung]]:
        return self._changes


################################################################
class SollmietenTableModel( SollzahlungenTableModel ):
    def __init__( self, sollList: List[XSollzahlung] ):
        SollzahlungenTableModel.__init__( self, sollList )
        self._numColumns: Tuple = (4, 5, 6)

    def isNumColumn( self, col:int ) -> bool:
        return col in self._numColumns

    def getKeyList( self ) -> Tuple[str]:
        return ( "mobj_id", "mv_id", "von", "bis", "netto", "nkv", "brutto", "bemerkung" )

    def getHeaders( self ) -> Tuple[str]:
        return ( "Objekt", "Mieter", "von", "bis", "netto", "NKV", "Brutto", "Bemerkung" )

    def getRow( self, x:XSollMiete ):
        for r in range( len( self.sollList ) ):
            e: XSollMiete = self.sollList[r]
            if e.sm_id == x.sm_id:
                return r
        raise Exception( "SollmietenTableModel.getRow(): can't find sm_id %d" % (x.sm_id) )

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

    def getRow( self, x:XSollHausgeld ):
        for r in range( len( self.sollList ) ):
            e: XSollHausgeld = self.sollList[r]
            if e.shg_id == x.shg_id:
                return r
        raise Exception( "SollHGVTableModel.getRow(): can't find shg_id %d" % (x.shg_id) )

    # def writeChangeLog( self, actionId:constants.tableAction, x:XSollzahlung ):
    #     x:XSollHausgeld = x
    #     # todo

if __name__ == "__main__":
    x = XSollzahlung()
    l = [x,]
    m = SollzahlungenTableModel( l )
    m2 = SollmietenTableModel( l )