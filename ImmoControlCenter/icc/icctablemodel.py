from abc import abstractmethod, ABC
from functools import cmp_to_key

from PySide2.QtCore import QAbstractTableModel, SIGNAL, Qt
from typing import Any, List

class IccTableModel( QAbstractTableModel ):
    def __init__(self):
        QAbstractTableModel.__init__( self )
        self._sortable = False
        self._sort_col = -1
        self._sort_reverse = False

    def getChanges( self ) -> Any:
        return None

    def setSortable( self, sortable:bool=True ):
        self._sortable = sortable

    def sort( self, col:int, order: Qt.SortOrder=Qt.SortOrder.AscendingOrder ) -> None:
        if not self._sortable: return
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self._sort_col = col
        self._sort_reverse = True if order == Qt.SortOrder.AscendingOrder else False
        sortedlist = sorted( self.getListToSort(), key=cmp_to_key( self.compare ) )
        self.receiveSortedList( sortedlist )
        self.emit(SIGNAL("layoutChanged()"))

    @abstractmethod
    def isChanged( self ) -> bool:
        pass

    @abstractmethod
    def getListToSort( self ) -> List:
        pass

    @abstractmethod
    def receiveSortedList( self, li:List ) -> None:
        pass

    @abstractmethod
    def compare( self, x1:Any, x2:Any ) -> int:
        pass

    @abstractmethod
    def clearChanges( self ):
        pass
