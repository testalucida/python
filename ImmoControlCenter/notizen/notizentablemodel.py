import copy
import numbers
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QBrush, QFont

import constants
from icctablemodel import IccTableModel
from interfaces import XNotiz


class NotizenTableModel( IccTableModel ):
    def __init__( self, notizenList:List[XNotiz] ):
        IccTableModel.__init__( self )
        self._notizenList:List[XNotiz] = notizenList
        self._keyHeaderMapper = {
            "erfasst am": "erfasst_am",
            "Bezug": "bezug",
            "Überschrift": "ueberschrift",
            "Text": "text",
            "erledigt": "erledigt",
            "Last Write Acccess": "lwa"
        }
        self._headers = list( self._keyHeaderMapper.keys() )

        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XNotiz]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "INSERT": List[XNotiz],
            "UPDATE": List[XNotiz],
            "DELETE": List[XNotiz]
        }
        """
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        # self._sortable = False

    def isChanged( self ) -> bool:
        for k, v in self._changes.items():
            if len( v ) > 0: return True
        return False

    # def setSortable( self, sortable:bool=True ):
    #     self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._notizenList )

    def getXNotiz( self, row:int ) -> XNotiz:
        return self._notizenList[row]

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self.getHeaders() )

    def getHeaders( self ) -> List[str]:
        return self._headers

    def duplicate( self, x: XNotiz ) -> XNotiz:
        """
        duplicates x and returns the duplicate copy
        Raises an exception if x cannot be found in the list of XNotiz
        :param x:
        :return:
        """
        x2: XNotiz = copy.copy( x )
        x2.id = 0
        l = self._notizenList
        for i in range( len( l ) ):
            tmp: XNotiz = l[i]
            if tmp == x:
                l.insert( i, x2 )
                self._writeChangeLog( constants.tableAction.INSERT, x2 )
                self.layoutChanged.emit()
                return x2
        raise Exception( "Notiz mit ID = %d nicht in der Notizen-Liste gefunden." % ( x.notiz_id ) )

    def _writeChangeLog( self, actionId:constants.tableAction, x:XNotiz ) -> None:
        """
        Schreibt ein in-memory-Log der eingefügten und geänderten Sollzahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist:List[XNotiz] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._notizenList[indexrow]
        header = self._headers[indexcolumn]
        key = self._keyHeaderMapper.get( header )
        val = x.__dict__[key]
        return val

    def getAlignment( self, indexrow: int, indexcolumn: int ):
        return int( Qt.AlignLeft | Qt.AlignVCenter )

    def getForeground( self, indexrow:int, indexcolumn: int ) -> Any:
        return None

    def getFont( self, indexrow: int, indexcolumn: int ) -> Any:
        return None

    def getBackground( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self.getXNotiz( indexrow )
        if self.isXNotizInsertedOrUpdated( x ):
            return self._yellowBrush
        return None

    def isXNotizInsertedOrUpdated( self, x:XNotiz ):
        dictChanges = self.getChanges()
        if x in dictChanges["INSERT"]: return True
        if x in dictChanges["UPDATE"]: return True
        if x in dictChanges["DELETE"]: return True
        return False

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

    def insert( self, x: XNotiz ):
        self._notizenList.append( x )
        self._writeChangeLog( constants.tableAction.INSERT, x )
        self.layoutChanged.emit()

    def update( self, x: XNotiz ):
        l = self._notizenList
        cols = len( self.getHeaders() )
        row = self.getRow( x )
        idxfrom = self.index( row, 0 )
        idxbis = self.index( row, cols - 1 )
        if not self._isInChangeLog( x, constants.tableAction.INSERT ):
            self.writeChangeLog( constants.tableAction.UPDATE, x )
        self.dataChanged.emit( idxfrom, idxbis )

    def delete( self, x:XNotiz ) -> None:
        self._notizenList.remove( x )
        self._writeChangeLog( constants.tableAction.DELETE, x )
        self.layoutChanged.emit()

    def resetChanges( self ):
        for k in self._changes.keys():
            self._changes[k] = list()
        self.layoutChanged.emit()

    def getRow( self, x: XNotiz ) -> int:
        for r in range( len( self._notizenList ) ):
            e: XNotiz = self._notizenList[r]
            if e == x:
                return r
        raise Exception( "OffenePostenTableModel.getRow(): can't find id %d" % (x.opos_id ) )

    def _isInChangeLog( self, x:XNotiz, actionId:constants.tableAction ) -> bool:
        actionstring = constants.actionList[actionId]
        xlist: List[XNotiz] = self._changes[actionstring]
        return ( x in xlist )

    def _removeFromChangeLog( self, x:XNotiz, actionId:constants.tableAction ) -> bool:
        actionstring = constants.actionList[actionId]
        xlist: List[XNotiz] = self._changes[actionstring]
        xlist.remove( x )

    #@abstractmethod
    def writeChangeLog( self, actionId:constants.tableAction, x:XNotiz ):
        """
        Schreibt ein in-memory-Log der eingefügten, geänderten, gelöschten Zahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist: List[XNotiz] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

    def getChanges( self ) -> Dict[str, List[XNotiz]]:
        return self._changes

    def getListToSort( self ) -> List:
        return self._notizenList

    def receiveSortedList( self, li:List ) -> None:
        self._notizenList = li

    def compare( self, x1:XNotiz, x2:XNotiz ) -> int:
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
    l = list()
    x = XNotiz()

    l.append( x )

    x = XNotiz()

    l.append( x )

    model = NotizenTableModel( l )