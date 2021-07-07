import copy
import numbers
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any

from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QBrush, QFont

import constants
from icctablemodel import IccTableModel
from interfaces import XOffenerPosten


class OffenePostenTableModel( IccTableModel ):
    def __init__( self, oposList:List[XOffenerPosten] ):
        IccTableModel.__init__( self )
        self._oposList:List[XOffenerPosten] = oposList
        self._keyHeaderMapper = {
            "erfasst am": "erfasst_am",
            "Debitor/Kreditor": "debi_kredi",
            "Betrag": "betrag",
            "davon beglichen": "betrag_beglichen",
            "letzte Buchung": "letzte_buchung_am",
            "Bemerkung": "bemerkung"
        }
        self._headers = list( self._keyHeaderMapper.keys() )  # [ "erfasst am", "Debitor/Kreditor", "Betrag", "gebucht am", "bemerkung" ]

        # Änderungslog vorbereiten:
        self._changes:Dict[str, List[XOffenerPosten]] = {}
        for s in constants.actionList:
            self._changes[s] = list()
        """
        Aufbau von _changes:
        {
            "INSERT": List[XOffenerPosten],
            "UPDATE": List[XOffenerPosten],
            "DELETE": List[XOffenerPosten]
        }
        """
        self._greyBrush = QBrush( Qt.gray )
        self._redBrush = QBrush( Qt.red )
        self._yellowBrush = QBrush( Qt.yellow )
        self._boldFont = QFont( "Arial", 11, QFont.Bold )
        self._betragColumns = (2, 3)
        # self._sortable = False

    def isChanged( self ) -> bool:
        for k, v in self._changes.items():
            if len( v ) > 0: return True
        return False

    # def setSortable( self, sortable:bool=True ):
    #     self._sortable = sortable

    def rowCount( self, parent:QModelIndex=None ) -> int:
        return len( self._oposList )

    def getXOffenerPosten( self, row:int ) -> XOffenerPosten:
        return self._oposList[row]

    def columnCount( self, parent: QModelIndex = None ) -> int:
        return len( self.getHeaders() )

    def isNumColumn( self, col: int ) -> bool:
        return True if col in self._betragColumns else False

    def getHeaders( self ) -> List[str]:
        return self._headers

    def duplicate( self, x: XOffenerPosten ) -> XOffenerPosten:
        """
        duplicates x and returns the duplicate copy
        Raises an exception if x cannot be found in the list of XOffenerPosten
        :param x:
        :return:
        """
        x2: XOffenerPosten = copy.copy( x )
        x2.id = 0
        l = self._oposList
        for i in range( len( l ) ):
            tmp: XOffenerPosten = l[i]
            if tmp.id == x.id:
                l.insert( i, x2 )
                self._writeChangeLog( constants.tableAction.INSERT, x2 )
                self.layoutChanged.emit()
                return x2
        raise Exception( "Offenen Posten mit ID = %d nicht in der OPOS-Liste gefunden." % ( x.id ) )

    def _writeChangeLog( self, actionId:constants.tableAction, x:XOffenerPosten ) -> None:
        """
        Schreibt ein in-memory-Log der eingefügten und geänderten Sollzahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist:List[XOffenerPosten] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

    def getValue( self, indexrow: int, indexcolumn: int ) -> Any:
        x = self._oposList[indexrow]
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
        x = self.getXOffenerPosten( indexrow )
        if self.isXOffenerPostenInsertedOrUpdated( x ):
            return self._yellowBrush
        return None

    def isXOffenerPostenInsertedOrUpdated( self, x:XOffenerPosten ):
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

    def updateOrInsert( self, x:XOffenerPosten ):
        l = self._oposList
        cols = len( self.getHeaders() )
        if x.opos_id > 0:  # update of existing auszahlung
            row = self.getRow( x )
            cols = len( self.getHeaders() )
            idxfrom = self.index( row, 0 )
            idxbis = self.index( row, cols - 1 )
            self.writeChangeLog( constants.tableAction.UPDATE, x )
            self.dataChanged.emit( idxfrom, idxbis )
        else:
            l.append( x )
            self._writeChangeLog( constants.tableAction.INSERT, x )
            self.layoutChanged.emit()

    def delete( self, x:XOffenerPosten ) -> None:
        self._oposList.remove( x )
        self._writeChangeLog( constants.tableAction.DELETE, x )
        self.layoutChanged.emit()

    def resetChanges( self ):
        for k in self._changes.keys():
            self._changes[k] = list()
        self.layoutChanged.emit()

    def getRow( self, x: XOffenerPosten ) -> int:
        for r in range( len( self._oposList ) ):
            e: XOffenerPosten = self._oposList[r]
            if e.id == x.id:
                return r
        raise Exception( "OffenePostenTableModel.getRow(): can't find id %d" % (x.id ) )

    #@abstractmethod
    def writeChangeLog( self, actionId:constants.tableAction, x:XOffenerPosten ):
        """
        Schreibt ein in-memory-Log der eingefügten, geänderten, gelöschten Zahlungen.
        Dieses kann über getChanges() abgerufen werden.
        """
        actionstring = constants.actionList[actionId]
        xlist: List[XOffenerPosten] = self._changes[actionstring]
        if not x in xlist:
            xlist.append( x )

    def getChanges( self ) -> Dict[str, List[XOffenerPosten]]:
        return self._changes

    def getListToSort( self ) -> List:
        return self._oposList

    def receiveSortedList( self, li:List ) -> None:
        self._oposList = li

    def compare( self, x1:XOffenerPosten, x2:XOffenerPosten ) -> int:
        key = self.getKeyList()[self.sort_col]
        v1 = x1.__dict__[key]
        v2 = x2.__dict__[key]
        if isinstance( v1, str ):
            v1 = v1.lower()
            v2 = v2.lower()
        if v1 < v2: return -1 if self.sort_reverse else 1
        if v1 > v2: return 1 if self.sort_reverse else -1
        if v1 == v2: return 0


    # def writeChangeLog( self, actionId:constants.tableAction, x:XOffenerPosten ):
    #     x:XSollHausgeld = x
    #     # todo

if __name__ == "__main__":
    l = list()
    x = XOffenerPosten()
    x.opos_id = 1
    x.mv_id = "Müller"
    x.erfasst_am = "2021-06-03"
    x.betrag = "123.45"
    x.bemerkung = "steht aus"
    l.append( x )

    x = XOffenerPosten()
    x.id = 2
    x.mv_id = "Himpfelhuber-Förrenschmidt"
    x.erfasst_am = "2021-06-03"
    x.betrag = "123.45"
    x.bemerkung = "steht aus trotz sechzehnmaliger Mahnung und Drohung"
    l.append( x )

    model = OffenePostenTableModel( l )